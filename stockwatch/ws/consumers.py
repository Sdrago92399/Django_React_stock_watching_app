import json
import asyncio
from decimal import Decimal
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from stocks.models import Stock, WatchlistItem
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

# Custom serializer to convert Decimal128 and Decimal types to float
def custom_serializer(obj):
    try:
        # If using pymongo's Decimal128, it should have a to_decimal() method.
        from bson.decimal128 import Decimal128
        if isinstance(obj, Decimal128):
            return float(obj.to_decimal())
    except ImportError:
        # If not using pymongo, ignore this
        pass
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Parse the token from the query string
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        token = None
        if "token=" in query_string:
            token = query_string.split("token=")[-1]
        
        # Validate the token and get the user
        if token:
            try:
                decoded_token = AccessToken(token)
                user_id = decoded_token.get('user_id')
                self.user = await database_sync_to_async(User.objects.get)(id=user_id)
            except Exception as e:
                print(f"Token validation failed: {e}")
                self.user = AnonymousUser()
        else:
            self.user = AnonymousUser()

        # Close the connection if the user isn’t authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = f"stocks_{self.user.id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

        # Start sending updates
        asyncio.create_task(self.send_watchlist_updates())

    async def disconnect(self, close_code):
        # Leave room group upon disconnection
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Handle messages from the WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'subscribe_stock':
            symbol = text_data_json.get('symbol')
            await self.channel_layer.group_add(
                f"stock_{symbol}",
                self.channel_name
            )
        elif message_type == 'unsubscribe_stock':
            symbol = text_data_json.get('symbol')
            await self.channel_layer.group_discard(
                f"stock_{symbol}",
                self.channel_name
            )
    
    # Fetch the user's watchlist stocks from the database
    @database_sync_to_async
    def get_watchlist_stocks(self):
        watchlist = list(WatchlistItem.objects.filter(
            user=self.user
        ).select_related('stock').values(
            'stock__symbol',
            'stock__name',
            'stock__last_price',
            'stock__change_percent'
        ))
        return watchlist
    
    # Periodically send stock updates over the WebSocket
    async def send_watchlist_updates(self):
        try:
            while True:
                stocks = await self.get_watchlist_stocks()
                if stocks:
                    payload = json.dumps({
                        'type': 'watchlist_update',
                        'stocks': stocks
                    }, default=custom_serializer)
                    await self.send(text_data=payload)
                
                # Wait 5 seconds before the next update
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            # Gracefully handle task cancellation, if needed.
            pass
    
    # Handle stock update messages from the room group (if you send group messages)
    async def watchlist_update(self, event):
        stocks = event['stocks']
        await self.send(text_data=json.dumps({
            'type': 'watchlist_update',
            'stocks': stocks
        }, default=custom_serializer))
