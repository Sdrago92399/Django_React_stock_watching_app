from datetime import datetime
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from .models import Alert, AlertType
from stocks.services import StockService

class AlertService:
    """Service for checking and processing stock alerts"""
    
    def __init__(self):
        self.stock_service = StockService()
    
    def check_alert(self, alert):
        """Check if an alert condition is met"""
        if not alert.is_active or alert.is_triggered:
            return False
            
        # Get current stock data
        quote = self.stock_service.get_stock_quote(alert.stock.symbol)
        if not quote:
            return False
            
        # Check condition based on alert type
        is_triggered = False
        
        if alert.alert_type == AlertType.PRICE_ABOVE:
            is_triggered = quote['price'] > alert.threshold_value
            
        elif alert.alert_type == AlertType.PRICE_BELOW:
            is_triggered = quote['price'] < alert.threshold_value
            
        elif alert.alert_type == AlertType.PERCENT_CHANGE:
            is_triggered = abs(quote['change_percent']) >= alert.threshold_value
            
        elif alert.alert_type == AlertType.VOLUME_ABOVE:
            is_triggered = quote['volume'] > int(alert.threshold_value)
            
        # Update stock data
        if is_triggered:
            alert.stock.last_price = quote['price']
            alert.stock.change_percent = quote['change_percent']
            alert.stock.volume = quote['volume']
            alert.stock.save()
            
            alert.is_triggered = True
            alert.last_triggered_at = datetime.now()
            alert.save()
            
        return is_triggered
    
    def send_alert_notification(self, alert):
        """Send email notification for triggered alert"""
        stock = alert.stock
        user = alert.user
        
        if alert.alert_type == AlertType.PRICE_ABOVE:
            subject = f"Price Alert: {stock.symbol} is above ${alert.threshold_value}"
            message = f"Hi {user.username},\n\n"
            message += f"Your price alert for {stock.name} ({stock.symbol}) has been triggered.\n"
            message += f"Current price: ${stock.last_price} is above your target of ${alert.threshold_value}.\n\n"
            message += f"Change: {stock.change_percent}%\n"
            message += f"Volume: {stock.volume}\n\n"
            message += "Best regards,\nStock Watchlist Alert System"
            
        elif alert.alert_type == AlertType.PRICE_BELOW:
            subject = f"Price Alert: {stock.symbol} is below ${alert.threshold_value}"
            message = f"Hi {user.username},\n\n"
            message += f"Your price alert for {stock.name} ({stock.symbol}) has been triggered.\n"
            message += f"Current price: ${stock.last_price} is below your target of ${alert.threshold_value}.\n\n"
            message += f"Change: {stock.change_percent}%\n"
            message += f"Volume: {stock.volume}\n\n"
            message += "Best regards,\nStock Watchlist Alert System"
            
        elif alert.alert_type == AlertType.PERCENT_CHANGE:
            subject = f"Change Alert: {stock.symbol} moved by {stock.change_percent}%"
            message = f"Hi {user.username},\n\n"
            message += f"Your percent change alert for {stock.name} ({stock.symbol}) has been triggered.\n"
            message += f"Current change: {stock.change_percent}% has exceeded your threshold of {alert.threshold_value}%.\n\n"
            message += f"Current price: ${stock.last_price}\n"
            message += f"Volume: {stock.volume}\n\n"
            message += "Best regards,\nStock Watchlist Alert System"
            
        elif alert.alert_type == AlertType.VOLUME_ABOVE:
            subject = f"Volume Alert: {stock.symbol} volume is above {alert.threshold_value}"
            message = f"Hi {user.username},\n\n"
            message += f"Your volume alert for {stock.name} ({stock.symbol}) has been triggered.\n"
            message += f"Current volume: {stock.volume} has exceeded your threshold of {alert.threshold_value}.\n\n"
            message += f"Current price: ${stock.last_price}\n"
            message += f"Change: {stock.change_percent}%\n\n"
            message += "Best regards,\nStock Watchlist Alert System"
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        return True
    
    def process_alerts(self):
        """Process all active alerts"""
        active_alerts = Alert.objects.filter(is_active=True, is_triggered=False)
        
        for alert in active_alerts:
            if self.check_alert(alert):
                self.send_alert_notification(alert)