from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from alerts.models import Alert, AlertType
from alerts.serializers import AlertSerializer
from stocks.models import Stock
from stocks.services import StockService

class AlertViewSetTestCase(APITestCase):
    """Test cases for AlertViewSet"""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)  # Authenticate the test client

        # Create test stock
        self.stock = Stock.objects.create(symbol='AAPL', name='Apple Inc.')

        # Create test alert
        self.alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type=AlertType.PRICE_ABOVE,  # Updated to match AlertType
            threshold_value=150.00,
            is_active=True,
            is_triggered=False
        )

    def assertResponse(self, response, expected_status):
        """Helper to print only the error message on failure"""
        if response.status_code != expected_status:
            print(f"Error Message: {response.data.get('error', response.data)}")
        self.assertEqual(response.status_code, expected_status)

    def test_get_user_alerts(self):
        """Test retrieving the authenticated user's alerts"""
        response = self.client.get('/api/alerts/')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_alert(self):
        """Test creating a new alert"""
        StockService.get_or_create_stock = lambda _, symbol: self.stock  # Mock service call

        response = self.client.post('/api/alerts/', {
            'alert_type': AlertType.PRICE_BELOW,  # Updated to match AlertType
            'threshold_value': 120.0
        }, format='json')
        self.assertResponse(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['alert_type'], AlertType.PRICE_BELOW)

    def test_create_price_alert(self):
        """Test creating a price alert for a stock"""
        StockService.get_or_create_stock = lambda _, symbol: self.stock  # Mock service call

        response = self.client.post('/api/alerts/create_price_alert/', {
            'symbol': 'AAPL',
            'alert_type': AlertType.PRICE_ABOVE,  # Updated to match AlertType
            'threshold_value': 200.00
        }, format='json')
        self.assertResponse(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['threshold_value'], "200.00")

    def test_toggle_active(self):
        """Test toggling the active status of an alert"""
        response = self.client.post(f'/api/alerts/{self.alert.id}/toggle_active/')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], not self.alert.is_active)

    def test_reset_alert(self):
        """Test resetting a triggered alert"""
        self.alert.is_triggered = True
        self.alert.save()

        response = self.client.post(f'/api/alerts/{self.alert.id}/reset/')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertEqual(response.data['is_triggered'], False)

    def test_reset_non_triggered_alert(self):
        """Test resetting a non-triggered alert"""
        response = self.client.post(f'/api/alerts/{self.alert.id}/reset/')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Alert has not been triggered yet')
