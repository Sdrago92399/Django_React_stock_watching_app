import os
import json
import requests
from decimal import Decimal
from django.conf import settings
from .models import Stock
  
class StockService:
    """Service for interacting with the Alpha Vantage Stock API"""
    
    def __init__(self):
        self.api_key = settings.STOCK_API_KEY
        self.base_url = settings.STOCK_API_BASE_URL
        
    def search_stocks(self, query):
        """Search for stocks by symbol or name"""
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': query,
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        print(data)
        
        if 'bestMatches' not in data:
            return []
            
        results = []
        for match in data['bestMatches']:
            results.append({
                'symbol': match['1. symbol'],
                'name': match['2. name'],
                'type': match['3. type'],
                'region': match['4. region'],
                'currency': match['8. currency']
            })
            
        return results
    
    def get_stock_quote(self, symbol):
        """Get real-time quote for a stock"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        if 'Global Quote' not in data or not data['Global Quote']:
            return None
            
        quote = data['Global Quote']
        return {
            'symbol': quote['01. symbol'],
            'price': Decimal(quote['05. price']),
            'change': Decimal(quote['09. change']),
            'change_percent': Decimal(quote['10. change percent'].rstrip('%')),
            'volume': int(quote['06. volume']),
            'latest_trading_day': quote['07. latest trading day']
        }

    def combine_data(self, query):
        """Search stocks and combine with real-time quotes"""
        matches = self.search_stocks(query)
        combined_results = []

        for match in matches:
            quote = self.get_stock_quote(match['symbol'])
            combined_results.append({
                **match,        # Include all details from `search_stocks`
                'quote': quote  # Include real-time stock quote data
            })

        return combined_results
        
    def get_intraday_data(self, symbol, interval='5min'):
        """Get intraday time series data"""
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        time_series_key = f"Time Series ({interval})"
        if time_series_key not in data:
            return []
            
        time_series = data[time_series_key]
        result = []
        
        for timestamp, values in time_series.items():
            result.append({
                'timestamp': timestamp,
                'open': Decimal(values['1. open']),
                'high': Decimal(values['2. high']),
                'low': Decimal(values['3. low']),
                'close': Decimal(values['4. close']),
                'volume': int(values['5. volume'])
            })
            
        return result
    
    def update_stock_data(self, stock):
        """Update stock data in the database"""
        quote = self.get_stock_quote(stock.symbol)
        
        if not quote:
            return False
            
        stock.last_price = quote['price']
        stock.change_percent = quote['change_percent']
        stock.volume = quote['volume']
        stock.save()
        
        return True
        
    def get_or_create_stock(self, symbol):
        """Get or create a stock in the database"""
        try:
            print(symbol)
            stock = Stock.objects.get(symbol=symbol)
            self.update_stock_data(stock)
            return stock
        except Stock.DoesNotExist:
            # Get stock details
            search_results = self.search_stocks(symbol)
            if not search_results:
                return None
                
            # Find exact match
            stock_data = None
            for result in search_results:
                if result['symbol'].upper() == symbol.upper():
                    stock_data = result
                    break
                    
            if not stock_data:
                return None
                
            # Get quote
            quote = self.get_stock_quote(symbol)
            if not quote:
                return None
                
            # Create new stock
            stock = Stock.objects.create(
                symbol=symbol,
                name=stock_data['name'],
                last_price=quote['price'],
                change_percent=quote['change_percent'],
                volume=quote['volume'],
                market_cap=0  # We'll need to get this from a different API endpoint
            )
            
            return stock