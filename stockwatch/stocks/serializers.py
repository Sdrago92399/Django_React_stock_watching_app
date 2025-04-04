from rest_framework import serializers
from .models import Stock, WatchlistItem

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'last_price', 'change_percent', 'volume', 'market_cap', 'updated_at']

class WatchlistItemSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    symbol = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = WatchlistItem
        fields = ['id', 'stock', 'symbol', 'added_at', 'notes']
        read_only_fields = ['added_at']