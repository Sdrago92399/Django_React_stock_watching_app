from rest_framework import serializers
from .models import Alert
from stocks.serializers import StockSerializer

class AlertSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    symbol = serializers.CharField(write_only=True, required=False)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'stock', 'symbol', 'alert_type', 'alert_type_display',
            'threshold_value', 'is_active', 'is_triggered',
            'created_at', 'last_triggered_at'
        ]
        read_only_fields = ['created_at', 'last_triggered_at', 'is_triggered']