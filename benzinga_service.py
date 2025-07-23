import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

class BenzingaService:
    """Service for accessing Benzinga premium news via Polygon API with quality scoring."""
    
    def __init__(self):
        """Initialize Benzinga via Polygon service."""
        self.api_key = Config.POLYGON_API_KEY  # Using Polygon key for Benzinga access
        self.base_url = "https://api.polygon.io"
        
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY not found in configuration. Please add your Polygon API key with Benzinga subscription.")
    
    def get_articles_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get Benzinga news articles via Polygon for a specific date range.
        
        Args:
            start_date: Start date for article search
            end_date: End date for article search
            
        Returns:
            List of high-quality Benzinga article dictionaries
        """
        # Use the working endpoint and parameters from your test
        endpoint = "/benzinga/v1/news"
        params = {
            "apiKey": self.api_key,  # ✅ Exact match to your working code
            "limit": Config.MAX_ARTICLES,
            "sort": "published.desc",  # ✅ Exact match to your working code
            # ✅ Add working date parameters
            "published.gte": start_date.strftime("%Y-%m-%d"),
            "published.lte": end_date.strftime("%Y-%m-%d")
        }
        
        raw_articles = self._make_request(endpoint, params)
        
        # Convert to consistent format and filter using quality scoring
        high_quality_articles = []
        for article in raw_articles:
            # Use quality scoring system to filter out noise
            if self._is_valuable_content(article):
                converted_article = self._normalize_benzinga_format(article)
                high_quality_articles.append(converted_article)
        
        return high_quality_articles
    
    def _is_valuable_content(self, article: Dict) -> bool:
        """Filter articles using quality scoring system."""
        score = self._score_article_quality(article)
        return score >= 60  # Only keep articles with 60+ quality score
    
    def _score_article_quality(self, article: Dict) -> int:
        """Score article quality from 0-100 based on professional relevance."""
        title = article.get('title', '').lower()
        teaser = article.get('teaser', '').lower()
        tickers = article.get('tickers', [])
        
        score = 50  # Base score
        
        # NEGATIVE SCORING - Reduce points for low-value content
        
        # Immediate disqualifiers (-100 points)
        disqualifiers = [
            'beef: it\'s what\'s for dinner',
            'correction:',
            'ticker is',
            'what\'s for dinner',
            'if you can afford it',
            'says \'i want to cry\'',
            'meme mania',
            'short squeeze frenzy',
            'portnoy says',
            'jim cramer says'
        ]
        
        if any(phrase in title for phrase in disqualifiers):
            return 0  # Immediate rejection
        
        # Major penalties (-30 points each)
        major_penalties = [
            'trading halt',
            'halt news pending',
            'here\'s how much $',
            'if you invested $',
            'years ago would be worth',
            'celebrity says',
            'influencer says',
            'would have made owning',
            'invested in this stock',
            'owning this stock'
        ]
        
        for penalty in major_penalties:
            if penalty in title:
                score -= 30
        
        # Medium penalties (-15 points each)
        medium_penalties = [
            'deep dive into',
            'what happened?',
            'stock tumbled',
            'stock spikes',
            'unveils',
            'reaffirms commitment',
            'has received',
            'follow-on order'
        ]
        
        for penalty in medium_penalties:
            if penalty in title:
                score -= 15
        
        # Minor penalties (-10 points each)
        minor_penalties = [
            'preview:',
            'analyst perspectives',
            'maintains equal-weight',
            'maintains price target',
            'maintains neutral'
        ]
        
        for penalty in minor_penalties:
            if penalty in title:
                score -= 10
        
        # POSITIVE SCORING - Add points for valuable content
        
        # High-value financial terms (+20 points each)
        high_value_terms = [
            'earnings',
            'revenue',
            'profit',
            'quarterly results',
            'eps',
            'beats estimates',
            'misses estimates',
            'guidance raised',
            'guidance lowered',
            'fed',
            'federal reserve',
            'interest rates',
            'monetary policy',
            'inflation',
            'gdp',
            'economic data'
        ]
        
        for term in high_value_terms:
            if term in title or term in teaser:
                score += 20
        
        # Medium-value terms (+15 points each)
        medium_value_terms = [
            'merger',
            'acquisition',
            'partnership',
            'joint venture',
            'ipo',
            'upgraded',
            'downgraded',
            'price target',
            'analyst',
            'rating',
            'policy',
            'regulation',
            'china',
            'trade'
        ]
        
        for term in medium_value_terms:
            if term in title or term in teaser:
                score += 15
        
        # Ticker bonus (+10 points if has relevant tickers)
        if len(tickers) > 0:
            score += 10
        
        # Major company bonus (+15 points)
        major_companies = [
            'apple', 'microsoft', 'google', 'alphabet', 'amazon', 'tesla', 'meta',
            'nvidia', 'jpmorgan', 'berkshire', 'alibaba', 'tencent', 'bezos', 'spacex'
        ]
        
        if any(company in title for company in major_companies):
            score += 15
        
        # Length bonus (substantial content)
        if len(title) >= 60:  # Detailed titles usually indicate substantial content
            score += 10
        
        # Professional publisher bonus
        publisher = article.get('publisher', {}).get('name', '').lower()
        if 'benzinga' in publisher:
            score += 5
        
        return max(0, min(100, score))  # Clamp between 0-100
    
    def get_recent_articles(self, days_back: int = 7) -> List[Dict]:
        """
        Get recent Benzinga articles from the past N days.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of article dictionaries
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return self.get_articles_by_date_range(start_date, end_date)
    
    def get_articles_by_tickers(self, tickers: List[str], days_back: int = 7) -> List[Dict]:
        """
        Get Benzinga articles for specific tickers.
        
        Args:
            tickers: List of ticker symbols
            days_back: Number of days to look back
            
        Returns:
            List of article dictionaries
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Get articles for date range first, then filter by tickers
        all_articles = self.get_articles_by_date_range(start_date, end_date)
        
        # Filter articles that mention the specified tickers
        ticker_articles = []
        for article in all_articles:
            article_tickers = article.get('tickers', [])
            if any(ticker.upper() in [t.upper() for t in article_tickers] for ticker in tickers):
                ticker_articles.append(article)
        
        return ticker_articles
    
    def _normalize_benzinga_format(self, article: Dict) -> Dict:
        """
        Normalize Benzinga article format from Polygon API.
        
        Args:
            article: Article from Polygon/Benzinga API
            
        Returns:
            Normalized article dictionary with source URL
        """
        # Map Polygon/Benzinga fields to our standard format
        normalized = {
            'id': article.get('id', article.get('benzinga_id', '')),
            'title': article.get('title', ''),
            'teaser': article.get('teaser', article.get('summary', article.get('description', ''))),
            'body': article.get('content', article.get('body', '')),
            'created': article.get('published', article.get('published_utc', article.get('date', ''))),
            'url': article.get('url', article.get('article_url', '')),
            'author': article.get('author', ''),
            'tickers': article.get('tickers', []),
            
            # Benzinga-specific fields
            'publisher': {'name': 'Benzinga'},  # Set explicitly since this is Benzinga content
            'insights': article.get('insights', []),
            'keywords': article.get('keywords', article.get('tags', [])),
            'amp_url': article.get('amp_url', ''),
            'image_url': article.get('image_url', ''),
            
            # Metadata
            'source': 'benzinga_via_polygon',
            'has_sentiment': bool(article.get('insights') or article.get('sentiment'))
        }
        
        # Ensure we have a teaser
        if not normalized['teaser'] and normalized['body']:
            normalized['teaser'] = normalized['body'][:200] + "..." if len(normalized['body']) > 200 else normalized['body']
        elif not normalized['teaser'] and normalized['title']:
            normalized['teaser'] = normalized['title']
        
        return normalized
    
    def categorize_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize articles by major themes.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Dictionary with categorized articles
        """
        themes = {
            'earnings': [],
            'fed_policy': [],
            'trade_tensions': [],
            'tech_developments': [],
            'geopolitical': [],
            'market_movements': [],
            'deals_ma': [],
            'china_sea': [],
            'crypto': [],
            'other': []
        }
        
        for article in articles:
            title = article.get('title', '').lower()
            teaser = article.get('teaser', '').lower()
            keywords = ' '.join(article.get('keywords', [])).lower()
            tickers = [t.lower() for t in article.get('tickers', [])]
            
            text = f"{title} {teaser} {keywords}"
            
            categorized = False
            
            # Enhanced China/SEA detection (priority for Asia focus)
            china_indicators = [
                'china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'hong kong',
                'taiwan', 'singapore', 'japan', 'korea', 'asia', 'asian',
                'alibaba', 'tencent', 'baidu', 'nio', 'xpeng', 'li auto',
                'hang seng', 'nikkei', 'shanghai composite', 'pboc',
                'yuan', 'rmb', 'trade war', 'tariff', 'supply chain'
            ]
            china_tickers = ['baba', 'tcehy', 'jd', 'bidu', 'nio', 'xpev', 'li']
            
            if (any(indicator in text for indicator in china_indicators) or 
                any(ticker in tickers for ticker in china_tickers)):
                themes['china_sea'].append(article)
                categorized = True
            
            # Earnings
            if any(word in text for word in ['earnings', 'revenue', 'profit', 'quarterly', 'eps', 'q1', 'q2', 'q3', 'q4', 'fiscal']):
                themes['earnings'].append(article)
                categorized = True
            
            # Fed/Monetary Policy
            if any(word in text for word in ['fed', 'federal reserve', 'interest rates', 'powell', 'monetary', 'inflation', 'rate cut', 'rate hike', 'fomc']):
                themes['fed_policy'].append(article)
                categorized = True
            
            # Trade/Tariffs
            if any(word in text for word in ['tariff', 'trade war', 'trade deal', 'import', 'export', 'sanctions', 'trade deficit', 'wto']):
                themes['trade_tensions'].append(article)
                categorized = True
            
            # Technology
            if any(word in text for word in ['ai', 'artificial intelligence', 'tech', 'semiconductor', 'chip', 'software', 'hardware', 'innovation', 'cloud', 'saas']):
                themes['tech_developments'].append(article)
                categorized = True
            
            # Geopolitical
            if any(word in text for word in ['trump', 'election', 'government', 'policy', 'regulation', 'biden', 'congress', 'senate', 'political']):
                themes['geopolitical'].append(article)
                categorized = True
            
            # Market movements
            if any(word in text for word in ['surge', 'plunge', 'rally', 'crash', 'soar', 'tumble', 'spike', 'drop', 'gain', 'loss', 'bull', 'bear']):
                themes['market_movements'].append(article)
                categorized = True
            
            # M&A/Deals
            if any(word in text for word in ['merger', 'acquisition', 'deal', 'buyout', 'takeover', 'm&a', 'partnership', 'joint venture']):
                themes['deals_ma'].append(article)
                categorized = True
            
            # Crypto
            if any(word in text for word in ['bitcoin', 'crypto', 'blockchain', 'ethereum', 'btc', 'eth', 'cryptocurrency', 'digital currency', 'defi']):
                themes['crypto'].append(article)
                categorized = True
            
            if not categorized:
                themes['other'].append(article)
        
        return themes
    
    def extract_key_stories(self, themes: Dict[str, List[Dict]], limit: int = 3) -> Dict[str, List[Dict]]:
        """
        Extract the most important stories from each theme.
        
        Args:
            themes: Categorized articles dictionary
            limit: Maximum stories per theme
            
        Returns:
            Dictionary with top stories per theme
        """
        key_stories = {}
        
        for theme, articles in themes.items():
            if not articles:
                continue
            
            # Score articles based on importance
            scored_articles = []
            for article in articles:
                score = self._score_article_importance(article)
                scored_articles.append((article, score))
            
            # Sort by score and take top stories
            scored_articles.sort(key=lambda x: x[1], reverse=True)
            key_stories[theme] = [article for article, score in scored_articles[:limit]]
        
        return key_stories
    
    def _score_article_importance(self, article: Dict) -> int:
        """
        Score article importance (enhanced for Benzinga content).
        
        Args:
            article: Article dictionary
            
        Returns:
            Importance score (higher is more important)
        """
        score = 0
        title = article.get('title', '').lower()
        teaser = article.get('teaser', '').lower()
        keywords = ' '.join(article.get('keywords', [])).lower()
        tickers = article.get('tickers', [])
        text = f"{title} {teaser} {keywords}"
        
        # Major company mentions (including Chinese companies)
        major_companies = [
            'apple', 'microsoft', 'google', 'amazon', 'tesla', 'meta', 'nvidia',
            'jpmorgan', 'johnson', 'walmart', 'berkshire', 'visa', 'mastercard',
            'alibaba', 'tencent', 'baidu', 'nio', 'xpeng', 'li auto',
            'aapl', 'msft', 'googl', 'amzn', 'tsla', 'nvda', 'jpm', 'baba', 'tcehy'
        ]
        score += sum(5 for company in major_companies if company in text)
        
        # Financial impact words
        impact_words = ['billion', 'million', 'record', 'historic', 'breakthrough', 'crisis', 'major', 'significant', 'beats estimates', 'misses estimates']
        score += sum(3 for word in impact_words if word in text)
        
        # Urgency indicators
        urgent_words = ['breaking', 'just in', 'urgent', 'alert', 'exclusive', 'update', 'latest', 'developing']
        score += sum(4 for word in urgent_words if word in text)
        
        # Benzinga premium content bonus
        score += 5  # All content from this endpoint is premium Benzinga
        
        # China/Asia bonus
        china_keywords = [
            'china', 'chinese', 'hong kong', 'taiwan', 'singapore', 'japan', 'korea',
            'alibaba', 'tencent', 'trade war', 'yuan', 'hang seng'
        ]
        if any(keyword in text for keyword in china_keywords):
            score += 4
        
        # Ticker relevance
        if len(tickers) > 0:
            score += min(len(tickers) * 3, 9)
        
        # Recency bonus
        try:
            created_time = datetime.fromisoformat(article.get('created', '').replace('Z', '+00:00'))
            hours_old = (datetime.now().astimezone() - created_time).total_seconds() / 3600
            if hours_old < 24:
                score += 5
            elif hours_old < 48:
                score += 3
            elif hours_old < 72:
                score += 1
        except:
            pass
        
        # Body content bonus (premium Benzinga has full articles)
        body_length = len(article.get('body', ''))
        if body_length > 500:
            score += 3
        if body_length > 1000:
            score += 3
        
        return score
    
    def _make_request(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """
        Make HTTP request to Polygon API for Benzinga content (using working parameters).
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            List of response data
        """
        if params is None:
            params = {}
        
        url = f"{self.base_url}{endpoint}"
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')
            req.add_header('User-Agent', 'Market-Research-Platform/1.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.getcode() != 200:
                    raise Exception(f"API request failed with status {response.getcode()}")
                
                data = response.read()
                result = json.loads(data.decode('utf-8'))
                
                # Handle Polygon API response format (based on your working code)
                if isinstance(result, dict):
                    if 'results' in result:
                        return result['results']
                    elif result.get('status') == 'OK' and 'data' in result:
                        return result['data']
                    else:
                        # Try to return the result as-is if it's not in expected format
                        return [result] if result else []
                elif isinstance(result, list):
                    return result
                else:
                    return []
        
        except urllib.error.HTTPError as e:
            if e.code == 403:
                raise Exception("Polygon API access denied. Check your Benzinga subscription status.")
            elif e.code == 404:
                raise Exception("Benzinga endpoint not found. Verify your subscription includes Benzinga news access.")
            else:
                raise Exception(f"Polygon API HTTP error: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"Polygon API connection error: {e.reason}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Polygon API response: {e}")
        except Exception as e:
            raise Exception(f"Polygon API error: {str(e)}")
    
    def get_api_status(self) -> Dict:
        """
        Check API status and Benzinga subscription.
        
        Returns:
            Status information dictionary
        """
        try:
            # Test Benzinga access via Polygon using working parameters
            endpoint = "/benzinga/v1/news"
            params = {
                "apiKey": self.api_key,
                "limit": 5,
                "sort": "published.desc"
            }
            
            test_articles = self._make_request(endpoint, params)
            
            return {
                'status': 'connected',
                'api_key_valid': True,
                'last_test': datetime.now().isoformat(),
                'sample_articles': len(test_articles),
                'api_type': 'benzinga_via_polygon_premium',
                'endpoint': f'{self.base_url}/benzinga/v1/news',
                'subscription': 'Benzinga Premium via Polygon',
                'features': ['full article body', 'premium content', 'quality scoring', 'intelligent filtering'],
                'test_response': 'success'
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'api_key_valid': False,
                'error': str(e),
                'last_test': datetime.now().isoformat(),
                'api_type': 'benzinga_via_polygon_premium',
                'test_response': 'failed'
            }