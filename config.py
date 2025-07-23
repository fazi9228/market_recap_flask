import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Flask application."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # API Keys
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
    BENZINGA_API_KEY = os.getenv('BENZINGA_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Application settings
    APP_NAME = "Market Research Platform"
    APP_VERSION = "1.1.0" # Version updated
    
    # Data refresh settings
    CACHE_TIMEOUT = 3600

    # Market data settings
    DEFAULT_MARKET_PERIOD = "5d"
    MAX_ARTICLES = 250 # Increased for broader coverage

    # Language options
    SUPPORTED_LANGUAGES = [
        'English',
        'Thai', 
        'Simplified Chinese',
        'Traditional Chinese',
        'Vietnamese'
    ]
    
    # --- MAJOR ASSET LISTS ---
    
    MAJOR_INDICES = [
        '^GSPC',     # S&P 500
        '^DJI',      # Dow Jones
        '^IXIC',     # NASDAQ
        '^HSI',      # Hang Seng (Hong Kong)
        '000001.SS', # Shanghai Composite
        '399001.SZ', # Shenzhen Component
        '^N225',     # Nikkei 225
        '^STI',      # Straits Times Index (Singapore)
        '^FTSE',     # FTSE 100
        '^GDAXI',    # DAX
    ]
    
    MAJOR_STOCKS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
        'JPM', 'JNJ', 'V', 'WMT', 'UNH', 'HD', 'PG', 'MA'
    ]

    # --- NEW CHINA & SEA ASSET LISTS ---
    
    CHINA_A_SHARES = [ # Shanghai & Shenzhen
        '600519.SS', # Kweichow Moutai
        '601318.SS', # Ping An Insurance
        '000001.SZ', # Ping An Bank
        '000651.SZ', # Gree Electric
        '300750.SZ'  # CATL
    ]

    HONG_KONG_STOCKS = [
        '0700.HK',   # Tencent Holdings
        '9988.HK',   # Alibaba Group
        '3690.HK',   # Meituan
        '1299.HK',   # AIA Group
        '0005.HK'    # HSBC Holdings
    ]
    
    SEA_STOCKS = [
        'D05.SI',    # DBS Group (Singapore)
        'SE',        # Sea Ltd (Singapore/US-listed)
        'BBCA.JK',   # Bank Central Asia (Indonesia)
        'TLK.N',     # Telkom Indonesia (Indonesia/US-listed)
        'ADVANC.BK'  # Advanced Info Service (Thailand)
    ]
    
    MAJOR_FOREX = [
        'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCNY=X', 'USDHKD=X', 'USDSGD=X',
        'AUDUSD=X', 'USDCAD=X', 'USDCHF=X', 'NZDUSD=X'
    ]
    
    @staticmethod
    def validate_api_keys():
        """Validate that required API keys are present."""
        missing_keys = []
        
        # Check for Polygon API key (primary method for Benzinga access)
        if not Config.POLYGON_API_KEY:
            missing_keys.append('POLYGON_API_KEY (required for Benzinga subscription)')
        
        if not Config.OPENAI_API_KEY:
            missing_keys.append('OPENAI_API_KEY')
            
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
        
        return True
    
    @staticmethod
    def get_news_api_info():
        """Get information about which news API is being used."""
        if Config.POLYGON_API_KEY:
            return {
                'api_type': 'benzinga_via_polygon_premium',
                'api_key': Config.POLYGON_API_KEY[:8] + '...',
                'cost': 'Premium subscription ($99/month)',
                'rate_limit': 'Higher limits with premium',
                'features': [
                    'premium Benzinga content', 
                    'full article body', 
                    'professional editorial quality',
                    'enhanced financial filtering',
                    'higher rate limits',
                    'China/Asia coverage'
                ],
                'endpoint': 'https://api.polygon.io/benzinga/v1/news',
                'subscription_status': 'active'
            }
        elif Config.BENZINGA_API_KEY:
            return {
                'api_type': 'benzinga_direct',
                'api_key': Config.BENZINGA_API_KEY[:8] + '...',
                'cost': 'Direct Benzinga subscription',
                'rate_limit': 'Based on subscription',
                'features': ['premium content', 'full article body', 'benzinga exclusive'],
                'endpoint': 'https://api.benzinga.com/api/v2/news',
                'subscription_status': 'fallback'
            }
        else:
            return {
                'api_type': 'none',
                'error': 'No news API key configured',
                'required': 'POLYGON_API_KEY with Benzinga subscription'
            }
    
    @staticmethod
    def get_subscription_status():
        """Get current subscription status and recommendations."""
        if Config.POLYGON_API_KEY:
            return {
                'status': 'premium_active',
                'provider': 'Polygon + Benzinga',
                'monthly_cost': '$99',
                'quality': 'professional_grade',
                'recommendation': 'optimal_setup',
                'features': [
                    '✅ Premium Benzinga content',
                    '✅ Full article bodies',
                    '✅ Professional editorial quality', 
                    '✅ Higher API rate limits',
                    '✅ Financial news filtering',
                    '✅ Email-ready reports'
                ]
            }
        else:
            return {
                'status': 'no_subscription',
                'provider': 'none',
                'monthly_cost': '$0',
                'quality': 'no_access',
                'recommendation': 'upgrade_required',
                'message': 'Add POLYGON_API_KEY with Benzinga subscription for premium content'
            }