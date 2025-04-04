from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from stocks.models import Stock, WatchlistItem
from stocks.services import StockService

class StockViewSetTestCase(APITestCase):
    """Test cases for StockViewSet"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)  # Authenticate the test client
        self.stock1 = Stock.objects.create(symbol='AAPL', name='Apple Inc')
        self.stock2 = Stock.objects.create(symbol='TSLA', name='Tesla Inc')

    def assertResponse(self, response, expected_status):
        """Helper to print only the error message on failure"""
        if response.status_code != expected_status:
            print(f"Error Message: {response.data.get('error', response.data)}")
        self.assertEqual(response.status_code, expected_status)

    def test_get_stocks(self):
        """Test retrieving all stocks"""
        response = self.client.get('/api/stocks/')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_stocks(self):
        """Test searching stocks by name"""
        response = self.client.get('/api/stocks/search/', {'q': 'Apple'})
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertTrue(any(stock['name'] == 'Apple Inc' for stock in response.data))

    def test_quote(self):
        """Test retrieving stock quote"""
        # Override StockService.get_stock_quote to return a fixed value
        StockService.get_stock_quote = lambda self, symbol: {'symbol': symbol, 'price': 150.0}
        response = self.client.get(f'/api/stocks/{self.stock1.id}/quote/')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertEqual(response.data.get('price'), 150.0)

    def test_intraday(self):
        """Test retrieving intraday data"""
        # Override StockService.get_intraday_data to return dummy data
        StockService.get_intraday_data = lambda self, symbol, interval: {'symbol': symbol, 'data': []}
        response = self.client.get(f'/api/stocks/{self.stock1.id}/intraday/')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertIn('data', response.data)


class WatchlistViewSetTestCase(APITestCase):
    """Test cases for WatchlistViewSet"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)  # Authenticate the test client
        self.stock = Stock.objects.create(symbol='AAPL', name='Apple Inc')

    def assertResponse(self, response, expected_status):
        """Helper to print only the error message on failure"""
        if response.status_code != expected_status:
            print(f"Error Message: {response.data.get('error', response.data)}")
        self.assertEqual(response.status_code, expected_status)

    def test_add_stock_to_watchlist(self):
        """Test adding a stock to the watchlist"""
        # Override get_or_create_stock to return self.stock
        StockService.get_or_create_stock = lambda _, symbol: self.stock
        response = self.client.post('/api/watchlist/add/', {'symbol': 'AAPL'}, format='json')
        self.assertResponse(response, status.HTTP_201_CREATED)
        # Assuming serializer returns a nested 'stock' object
        self.assertEqual(response.data.get('stock', {}).get('symbol'), 'AAPL')

    def test_add_duplicate_stock_to_watchlist(self):
        """Test adding a duplicate stock to the watchlist"""
        WatchlistItem.objects.create(user=self.user, stock=self.stock)
        response = self.client.post('/api/watchlist/add/', {'symbol': 'AAPL'}, format='json')
        response = self.client.post('/api/watchlist/add/', {'symbol': 'AAPL'}, format='json')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'Stock AAPL is already in your watchlist')

    def test_remove_stock_from_watchlist(self):
        """Test removing a stock from the watchlist"""
        WatchlistItem.objects.create(user=self.user, stock=self.stock)
        response = self.client.delete('/api/watchlist/remove/', {'symbol': 'AAPL'}, format='json')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertFalse(WatchlistItem.objects.filter(user=self.user, stock=self.stock).exists())

    def test_get_user_watchlist(self):
        """Test retrieving the user's watchlist"""
        WatchlistItem.objects.create(user=self.user, stock=self.stock)
        response = self.client.get('/api/watchlist/')
        self.assertResponse(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)