import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

class MarketService:
    """Service for fetching market data using yfinance."""
    
    def __init__(self):
        """Initialize market service."""
        self.major_stocks = Config.MAJOR_STOCKS
        self.major_forex = Config.MAJOR_FOREX
        self.major_indices = Config.MAJOR_INDICES
    
    def get_available_stocks(self) -> List[Dict]:
        """Get list of available stocks with names."""
        stocks_info = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation',
            'JPM': 'JPMorgan Chase & Co.',
            'JNJ': 'Johnson & Johnson',
            'V': 'Visa Inc.',
            'WMT': 'Walmart Inc.',
            'UNH': 'UnitedHealth Group',
            'HD': 'The Home Depot Inc.',
            'PG': 'Procter & Gamble Co.',
            'MA': 'Mastercard Inc.',
            'BAC': 'Bank of America Corp.',
            'XOM': 'Exxon Mobil Corporation',
            'CVX': 'Chevron Corporation',
            'KO': 'The Coca-Cola Company',
            'PEP': 'PepsiCo Inc.',
            'ABBV': 'AbbVie Inc.',
            'LLY': 'Eli Lilly and Company',
            'COST': 'Costco Wholesale Corp.',
            'MRK': 'Merck & Co. Inc.',
            'TMO': 'Thermo Fisher Scientific',
            'ACN': 'Accenture plc',
            'CSCO': 'Cisco Systems Inc.',
            'ABT': 'Abbott Laboratories',
            'VZ': 'Verizon Communications'
        }
        
        return [{'symbol': symbol, 'name': stocks_info.get(symbol, symbol)} 
                for symbol in self.major_stocks if symbol in stocks_info]
    
    def get_available_forex(self) -> List[Dict]:
        """Get list of available forex pairs with names."""
        forex_info = {
            'EURUSD=X': 'EUR/USD',
            'GBPUSD=X': 'GBP/USD', 
            'USDJPY=X': 'USD/JPY',
            'USDCNY=X': 'USD/CNY',
            'AUDUSD=X': 'AUD/USD',
            'USDCAD=X': 'USD/CAD',
            'USDCHF=X': 'USD/CHF',
            'NZDUSD=X': 'NZD/USD',
            'EURGBP=X': 'EUR/GBP',
            'EURJPY=X': 'EUR/JPY',
            'GBPJPY=X': 'GBP/JPY',
            'EURCHF=X': 'EUR/CHF'
        }
        
        return [{'symbol': symbol, 'name': forex_info.get(symbol, symbol)} 
                for symbol in self.major_forex if symbol in forex_info]
    
    def get_available_indices(self) -> List[Dict]:
        """Get list of available indices with names."""
        indices_info = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones Industrial Average',
            '^IXIC': 'NASDAQ Composite',
            '^RUT': 'Russell 2000',
            '^FTSE': 'FTSE 100',
            '^GDAXI': 'DAX',
            '^FCHI': 'CAC 40',
            '^HSI': 'Hang Seng Index (HK50)',
            '^N225': 'Nikkei 225',
            '^STOXX50E': 'Euro Stoxx 50',
            '^STI': 'Straits Times Index',
            '000001.SS': 'Shanghai Composite'
        }
        
        return [{'symbol': symbol, 'name': indices_info.get(symbol, symbol)} 
                for symbol in self.major_indices if symbol in indices_info]
    
    def get_current_market_data(self, stocks: List[str] = None, forex: List[str] = None, 
                               indices: List[str] = None) -> Dict:
        """Get current market data for selected assets."""
        result = {
            'stocks': [],
            'forex': [],
            'indices': []
        }
        
        if stocks:
            result['stocks'] = self._get_asset_data(stocks, 'stock')
        
        if forex:
            result['forex'] = self._get_asset_data(forex, 'forex')
            
        if indices:
            result['indices'] = self._get_asset_data(indices, 'index')
        
        return result
    
    def get_market_data_by_range(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get market performance data for specific date range."""
        market_data = {}
        
        # Get major indices performance
        for symbol in self.major_indices[:5]:  # Top 5 indices
            try:
                data = self._get_price_data(symbol, start_date, end_date)
                if data:
                    market_data[symbol] = data
            except Exception as e:
                continue
        
        return market_data
    
    def _get_asset_data(self, symbols: List[str], asset_type: str) -> List[Dict]:
        """Get data for a list of asset symbols."""
        assets_data = []
        name_mappings = self._get_name_mappings()
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")  # Get 1 month of data
                
                if hist.empty:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                
                # Calculate weekly change (7 days ago)
                weekly_change = self._calculate_percentage_change(hist, 7)
                
                # Calculate monthly change (30 days ago) 
                monthly_change = self._calculate_percentage_change(hist, 30)
                
                # Create Yahoo Finance link
                yahoo_symbol = symbol.replace('=X', '').replace('^', '%5E')
                if asset_type == 'forex':
                    yahoo_link = f"https://finance.yahoo.com/quote/{yahoo_symbol}=X"
                else:
                    yahoo_link = f"https://finance.yahoo.com/quote/{yahoo_symbol}"
                
                assets_data.append({
                    'symbol': symbol,
                    'name': name_mappings.get(symbol, symbol),
                    'current_price': round(current_price, 4) if current_price else None,
                    'weekly_change': weekly_change,
                    'monthly_change': monthly_change,
                    'link': yahoo_link,
                    'asset_type': asset_type
                })
                
            except Exception as e:
                # If we can't get data for a symbol, skip it
                continue
        
        return assets_data
    
    def _calculate_percentage_change(self, hist, days_back: int) -> Optional[float]:
        """Calculate percentage change over specified period."""
        try:
            if len(hist) < days_back:
                days_back = len(hist) - 1
            
            if days_back <= 0:
                return None
                
            current_price = hist['Close'].iloc[-1]
            past_price = hist['Close'].iloc[-(days_back + 1)]
            
            if past_price == 0:
                return None
                
            change = ((current_price - past_price) / past_price) * 100
            return round(change, 2)
            
        except (IndexError, ZeroDivisionError):
            return None
    
    def _get_price_data(self, symbol: str, start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """Get price data for a specific symbol and date range."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), 
                                end=(end_date + timedelta(days=1)).strftime("%Y-%m-%d"))
            
            if hist.empty or len(hist) < 2:
                return None
            
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            change_pct = ((end_price - start_price) / start_price) * 100
            
            return {
                'symbol': symbol,
                'start_price': round(start_price, 2),
                'end_price': round(end_price, 2),
                'change_pct': round(change_pct, 2),
                'period_days': len(hist)
            }
            
        except Exception:
            return None
    
    def _get_name_mappings(self) -> Dict[str, str]:
        """Get all name mappings for symbols."""
        mappings = {}
        
        # Add stock mappings
        stock_names = {
            'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corporation', 'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.', 'TSLA': 'Tesla Inc.', 'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation', 'JPM': 'JPMorgan Chase & Co.', 'JNJ': 'Johnson & Johnson',
            'V': 'Visa Inc.', 'WMT': 'Walmart Inc.', 'UNH': 'UnitedHealth Group',
            'HD': 'The Home Depot Inc.', 'PG': 'Procter & Gamble Co.', 'MA': 'Mastercard Inc.',
            'BAC': 'Bank of America Corp.', 'XOM': 'Exxon Mobil Corporation', 'CVX': 'Chevron Corporation',
            'KO': 'The Coca-Cola Company', 'PEP': 'PepsiCo Inc.', 'ABBV': 'AbbVie Inc.',
            'LLY': 'Eli Lilly and Company', 'COST': 'Costco Wholesale Corp.', 'MRK': 'Merck & Co. Inc.',
            'TMO': 'Thermo Fisher Scientific', 'ACN': 'Accenture plc', 'CSCO': 'Cisco Systems Inc.',
            'ABT': 'Abbott Laboratories', 'VZ': 'Verizon Communications'
        }
        mappings.update(stock_names)
        
        # Add forex mappings
        forex_names = {
            'EURUSD=X': 'EUR/USD', 'GBPUSD=X': 'GBP/USD', 'USDJPY=X': 'USD/JPY',
            'USDCNY=X': 'USD/CNY', 'AUDUSD=X': 'AUD/USD', 'USDCAD=X': 'USD/CAD',
            'USDCHF=X': 'USD/CHF', 'NZDUSD=X': 'NZD/USD', 'EURGBP=X': 'EUR/GBP',
            'EURJPY=X': 'EUR/JPY', 'GBPJPY=X': 'GBP/JPY', 'EURCHF=X': 'EUR/CHF'
        }
        mappings.update(forex_names)
        
        # Add index mappings
        index_names = {
            '^GSPC': 'S&P 500', '^DJI': 'Dow Jones Industrial Average', '^IXIC': 'NASDAQ Composite',
            '^RUT': 'Russell 2000', '^FTSE': 'FTSE 100', '^GDAXI': 'DAX', '^FCHI': 'CAC 40',
            '^HSI': 'Hang Seng Index (HK50)', '^N225': 'Nikkei 225', '^STOXX50E': 'Euro Stoxx 50',
            '^STI': 'Straits Times Index', '000001.SS': 'Shanghai Composite'
        }
        mappings.update(index_names)
        
        return mappings
    
    def get_market_status(self) -> Dict:
        """Get market status and connection test."""
        try:
            # Test with a simple stock query
            ticker = yf.Ticker('AAPL')
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                return {
                    'status': 'connected',
                    'last_test': datetime.now().isoformat(),
                    'test_symbol': 'AAPL',
                    'test_price': round(hist['Close'].iloc[-1], 2) if len(hist) > 0 else None
                }
            else:
                return {
                    'status': 'no_data',
                    'last_test': datetime.now().isoformat(),
                    'message': 'Connected but no data received'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_test': datetime.now().isoformat()
            }
