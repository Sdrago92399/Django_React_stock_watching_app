from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Stock, WatchlistItem
from .serializers import StockSerializer, WatchlistItemSerializer
from .services import StockService

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for stocks"""
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return stocks based on query parameters"""
        queryset = Stock.objects.all()
        symbol = self.request.query_params.get('symbol')
        
        if symbol:
            queryset = queryset.filter(symbol__iexact=symbol)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search for stocks by symbol or name"""
        query = request.query_params.get('q', '')
        if not query or len(query) < 2:
            return Response(
                {'error': 'Search query must be at least 2 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        service = StockService()
        results = service.combine_data(query)
        
        return Response(results)
    
    @action(detail=True, methods=['get'])
    def quote(self, request, pk=None):
        """Get real-time quote for a stock"""
        stock = self.get_object()
        
        service = StockService()
        quote = service.get_stock_quote(stock.symbol)
        
        if not quote:
            return Response(
                {'error': 'Could not retrieve quote for this stock'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response(quote)
    
    @action(detail=True, methods=['get'])
    def intraday(self, request, pk=None):
        """Get intraday data for a stock"""
        stock = self.get_object()
        interval = request.query_params.get('interval', '5min')
        
        service = StockService()
        data = service.get_intraday_data(stock.symbol, interval)
        
        if not data:
            return Response(
                {'error': 'Could not retrieve intraday data for this stock'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response(data)

class WatchlistViewSet(viewsets.ModelViewSet):
    """API endpoint for user watchlist"""
    serializer_class = WatchlistItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the authenticated user's watchlist items"""
        return WatchlistItem.objects.filter(
            user=self.request.user
        ).select_related('stock')
    
    def perform_create(self, serializer):
        """Add a stock to the user's watchlist"""
        symbol = self.request.data.get('symbol')
        if not symbol:
            return Response(
                {'error': 'Stock symbol is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get or create the stock
        service = StockService()
        stock = service.get_or_create_stock(symbol)
        
        if not stock:
            return Response(
                {'error': f'Stock with symbol {symbol} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Add to watchlist
        serializer.save(user=self.request.user, stock=stock)
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add a stock to the user's watchlist"""
        symbol = request.data.get('symbol')
        if not symbol:
            return Response(
                {'error': 'Stock symbol is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the stock is already in the watchlist
        service = StockService()
        stock = service.get_or_create_stock(symbol)
        
        if not stock:
            return Response(
                {'error': f'Stock with symbol {symbol} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Check if already in watchlist
        watchlist_item = WatchlistItem.objects.filter(
            user=request.user, stock=stock
        ).first()
        if watchlist_item:
            # Handle the absence of the item
            return Response(
                {'message': f'Stock {symbol} is already in your watchlist'},
                status=status.HTTP_200_OK
            )
            
        # Add to watchlist
        watchlist_item = WatchlistItem.objects.create(
            user=request.user,
            stock=stock,
            notes=request.data.get('notes', '')
        )
        
        serializer = self.get_serializer(watchlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['delete'])
    def remove(self, request):
        """Remove a stock from the user's watchlist"""
        symbol = request.data.get('symbol')
        if not symbol:
            return Response(
                {'error': 'Stock symbol is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Find the stock
        try:
            stock = Stock.objects.get(symbol__iexact=symbol)
        except Stock.DoesNotExist:
            return Response(
                {'error': f'Stock with symbol {symbol} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Remove from watchlist
        result = WatchlistItem.objects.filter(user=request.user, stock=stock).delete()
        if result[0] == 0:
            return Response(
                {'error': f'Stock {symbol} is not in your watchlist'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response(
            {'message': f'Stock {symbol} removed from watchlist'},
            status=status.HTTP_200_OK
        )