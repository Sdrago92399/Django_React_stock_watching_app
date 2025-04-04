from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Alert, AlertType
from .serializers import AlertSerializer
from stocks.models import Stock
from stocks.services import StockService

class AlertViewSet(viewsets.ModelViewSet):
    """API endpoint for user alerts"""
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the authenticated user's alerts"""
        return Alert.objects.filter(
            user=self.request.user
        ).select_related('stock')
    
    def perform_create(self, serializer):
        """Create a new alert"""
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
            
        # Create alert
        serializer.save(user=self.request.user, stock=stock)
    
    @action(detail=False, methods=['post'])
    def create_price_alert(self, request):
        """Create a price alert for a stock"""
        symbol = request.data.get('symbol')
        alert_type = request.data.get('alert_type')
        threshold_value = request.data.get('threshold_value')
        
        # Validate inputs
        if not symbol:
            return Response(
                {'error': 'Stock symbol is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not alert_type or alert_type not in [choice[0] for choice in AlertType.choices]:
            return Response(
                {'error': 'Valid alert type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not threshold_value:
            return Response(
                {'error': 'Threshold value is required'},
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

        # Create the alert
        alert = Alert.objects.create(
            user=request.user,
            stock=stock,
            alert_type=alert_type,
            threshold_value=threshold_value
        )
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of an alert"""
        alert = self.get_object()
        alert.is_active = not alert.is_active
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """Reset a triggered alert"""
        alert = self.get_object()
        
        if not alert.is_triggered:
            return Response(
                {'message': 'Alert has not been triggered yet'},
                status=status.HTTP_200_OK
            )
            
        alert.is_triggered = False
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)