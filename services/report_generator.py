from openai import OpenAI
from datetime import datetime
from typing import Dict, List
from config import Config

class ReportGenerator:
    """Professional newsletter generator with balanced fact-checking."""
    
    def __init__(self):
        """Initialize report generator."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in configuration")
    
    def generate_market_report(self, market_data: Dict, articles: List[Dict], 
                             start_date: datetime, end_date: datetime, 
                             language: str = 'English') -> str:
        """
        Generate professional newsletter with balanced approach.
        
        Args:
            market_data: Market performance data
            articles: News articles from Benzinga
            start_date: Report start date
            end_date: Report end date
            language: Target language for report
            
        Returns:
            Professional newsletter report
        """
        # Create engaging narrative report
        report = self._create_professional_newsletter(market_data, articles, start_date, end_date)
        
        # Translate if needed
        if language != 'English':
            report = self._translate_report(report, language)
        
        return report
    
    def _create_professional_newsletter(self, market_data: Dict, articles: List[Dict], 
                                      start_date: datetime, end_date: datetime) -> str:
        """Create professional newsletter with flowing narrative."""
        
        # Format basic info
        date_range = f"{start_date.strftime('%d')} - {end_date.strftime('%d %B %Y')}"
        trading_days = (end_date - start_date).days + 1
        
        # Prepare market data in readable format
        market_summary = self._format_market_data_narrative(market_data)
        
        # Prepare articles in thematic groups
        article_themes = self._organize_articles_by_themes(articles)
        
        # Create references
        references = self._format_references(articles)
        
        # Generate professional newsletter
        return self._generate_newsletter_content(
            date_range, trading_days, market_summary, article_themes, references, len(articles)
        )
    
    def _format_market_data_narrative(self, market_data: Dict) -> str:
        """Format market data for narrative presentation."""
        if not market_data:
            return "No market data available for this period."
        
        # Sort by performance
        sorted_markets = sorted(market_data.items(), key=lambda x: x[1].get('change_pct', 0), reverse=True)
        
        # Group by region for global perspective
        regions = {
            'Global Markets': [],
            'US Markets': [],
            'European Markets': [],
            'Asian Markets': []
        }
        
        for symbol, data in sorted_markets:
            name = self._get_readable_name(symbol)
            change = data.get('change_pct', 0)
            start_price = data.get('start_price', 0)
            end_price = data.get('end_price', 0)
            
            market_info = f"{name}: {change:+.2f}% (${start_price:.2f} to ${end_price:.2f})"
            
            # Categorize by region
            if symbol in ['^HSI', '^N225', '^STI', '000001.SS']:
                regions['Asian Markets'].append(market_info)
            elif symbol in ['^GSPC', '^DJI', '^IXIC', '^RUT']:
                regions['US Markets'].append(market_info)
            elif symbol in ['^FTSE', '^GDAXI', '^FCHI', '^STOXX50E']:
                regions['European Markets'].append(market_info)
            else:
                regions['Global Markets'].append(market_info)
        
        # Format for presentation
        formatted = []
        for region, markets in regions.items():
            if markets:
                formatted.append(f"{region}:")
                formatted.extend([f"  • {market}" for market in markets])
                formatted.append("")
        
        return "\n".join(formatted)
    
    def _organize_articles_by_themes(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize articles by themes with balanced coverage."""
        themes = {
            'earnings_corporate': [],
            'market_policy': [],
            'china_asia': [],
            'technology': [],
            'global_economy': [],
            'other_news': []
        }
        
        # Sort articles by date
        sorted_articles = sorted(articles, key=lambda x: x.get('created', ''), reverse=True)
        
        for article in sorted_articles:
            title = article.get('title', '').lower()
            teaser = article.get('teaser', '').lower()
            tickers = [t.lower() for t in article.get('tickers', [])]
            
            text = f"{title} {teaser}"
            categorized = False
            
            # Earnings and corporate news (priority)
            if any(word in text for word in ['earnings', 'revenue', 'profit', 'quarterly', 'eps', 'ceo', 'merger', 'acquisition']):
                themes['earnings_corporate'].append(article)
                categorized = True
            
            # Market policy and Fed news
            elif any(word in text for word in ['fed', 'policy', 'rate', 'inflation', 'central bank', 'monetary']):
                themes['market_policy'].append(article)
                categorized = True
            
            # China/Asia coverage (not forced, but included when relevant)
            elif (any(word in text for word in ['china', 'chinese', 'asia', 'hong kong', 'singapore', 'japan']) or
                  any(ticker in tickers for ticker in ['baba', 'tcehy', 'jd', 'bidu', 'nio'])):
                themes['china_asia'].append(article)
                categorized = True
            
            # Technology
            elif any(word in text for word in ['tech', 'ai', 'semiconductor', 'software', 'innovation']):
                themes['technology'].append(article)
                categorized = True
            
            # Global economy
            elif any(word in text for word in ['economy', 'gdp', 'growth', 'recession', 'trade']):
                themes['global_economy'].append(article)
                categorized = True
            
            if not categorized:
                themes['other_news'].append(article)
        
        return themes
    
    def _format_references(self, articles: List[Dict]) -> str:
        """Format references professionally."""
        if not articles:
            return "No sources available."
        
        sorted_articles = sorted(articles, key=lambda x: x.get('created', ''), reverse=True)[:10]
        
        refs = []
        for i, article in enumerate(sorted_articles, 1):
            title = article.get('title', 'No title')
            url = article.get('url', '')
            
            if url:
                refs.append(f"{i}. {title} - [Source]({url})")
            else:
                refs.append(f"{i}. {title}")
        
        return "\n".join(refs)
    
    def _generate_newsletter_content(self, date_range: str, trading_days: int, 
                                   market_summary: str, article_themes: Dict, 
                                   references: str, total_articles: int) -> str:
        """Generate flowing, professional newsletter content."""
        
        system_prompt = """
        You are a senior financial journalist writing for sophisticated institutional investors and high-net-worth individuals.
        
        WRITING STYLE:
        - Create flowing, engaging narratives that connect market events naturally
        - Use professional but accessible language (think Bloomberg Businessweek style)
        - Connect related developments into coherent stories
        - Focus on implications and context, not just facts
        - Write compelling section headers with relevant emojis
        - Balance global coverage - don't over-focus on any single region unless the data warrants it
        
        CONTENT APPROACH:
        - Use the provided market data and news articles as your foundation
        - You may draw reasonable connections between related events
        - Focus on what matters most to institutional investors
        - Include forward-looking perspective when supported by the news
        - Present balanced global coverage unless Asia/China news dominates the source material
        
        CRITICAL: NO TRADING ADVICE OR RECOMMENDATIONS:
        - Do NOT provide buy, sell, or hold recommendations for any stocks, currencies, or assets
        - Do NOT suggest specific trading strategies or investment actions
        - Do NOT give price predictions or target recommendations
        - Focus on reporting developments and their potential implications, not actionable advice
        - Use phrases like "developments suggest" or "market participants are watching" rather than "investors should"
        - Present information for educational and informational purposes only
        
        FACTUAL BOUNDARIES:
        - Use only companies and data points mentioned in the source material
        - When making connections, indicate if they're your analysis vs. stated facts
        - Don't invent specific numbers, percentages, or quotes not in the sources
        - If you're uncertain about a connection, use phrases like "this suggests" or "appears to indicate"
        """
        
        # Format article themes for AI with source links
        theme_summaries = []
        theme_names = {
            'earnings_corporate': '💼 Corporate Earnings & Developments',
            'market_policy': '🏛️ Central Bank & Policy Updates',
            'china_asia': '🇨🇳 Asia-Pacific Developments',
            'technology': '💻 Technology & Innovation',
            'global_economy': '🌍 Global Economic Trends',
            'other_news': '📰 Other Market News'
        }
        
        for theme_key, articles in article_themes.items():
            if articles:
                theme_name = theme_names.get(theme_key, theme_key)
                theme_summaries.append(f"\n{theme_name}:")
                for article in articles[:4]:  # Top 4 per theme
                    title = article.get('title', '')
                    teaser = article.get('teaser', '')
                    url = article.get('url', '')
                    
                    theme_summaries.append(f"• {title}")
                    if teaser:
                        theme_summaries.append(f"  Summary: {teaser}")
                    if url:
                        theme_summaries.append(f"  Source: {url}")
                    theme_summaries.append("")  # Empty line between articles
        
        articles_summary = "\n".join(theme_summaries)
        
        user_prompt = f"""
        Create a professional market newsletter for the period {date_range} ({trading_days} trading days).
        
        MARKET PERFORMANCE:
        {market_summary}
        
        KEY DEVELOPMENTS BY THEME (with source URLs for reference):
        {articles_summary}
        
        TOTAL ARTICLES ANALYZED: {total_articles}
        
        ---
        NEWSLETTER STRUCTURE:
        
        # Market Insights: {date_range}
        
        ## 📊 Executive Summary
        [Write 2-3 engaging paragraphs that capture the week's dominant themes and their significance for investors. Create a narrative that connects the major developments.]
        
        ## 📈 Market Performance Review
        [Analyze the market movements in context. Start with the best and worst performers, explain what drove the movements based on the news themes. Present in flowing narrative, not bullet points.]
        
        ## 💼 Corporate & Earnings Developments
        [Cover the corporate news and earnings stories. Group related developments and explain their broader implications.]
        
        ## 🏛️ Policy & Economic Updates
        [Cover central bank news, policy changes, and economic data. Explain the market implications.]
        
        ## 🌏 Global Market Themes
        [Cover other significant themes including any Asia-Pacific developments, technology news, etc. Only create this section if there's substantial content.]
        
        ## 🔮 Looking Ahead
        [Based on the developments covered, provide perspective on what investors should watch for. Keep this grounded in the themes that emerged from the news.]
        
        ## 📚 Sources
        {references}
        
        WRITING GUIDELINES:
        - Create smooth transitions between topics
        - Use specific data points from the market performance
        - Connect news events to market movements where logical
        - Write in flowing paragraphs, not bullet points (except in Sources)
        - Balance coverage based on the actual news flow - don't force regional focus
        - Do NOT include source URLs within the narrative text - keep the content clean and readable
        - All source verification should be in the Sources section only
        - Target ~1000-1200 words for comprehensive coverage
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2800,
                temperature=0.7  # Balanced creativity for engaging writing
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating newsletter: {str(e)}"
    
    def _translate_report(self, report: str, target_language: str) -> str:
        """Translate newsletter while preserving original references."""
        language_map = {
            'Thai': 'Thai',
            'Simplified Chinese': 'Simplified Chinese',
            'Traditional Chinese': 'Traditional Chinese', 
            'Vietnamese': 'Vietnamese'
        }
        
        if target_language not in language_map:
            return report
        
        # Split report to preserve references section
        references_patterns = [
            '## 📚 Sources',
            '## 📚 References', 
            '## Sources',
            '## References'
        ]
        
        references_section = ""
        main_content = report
        
        # Find and extract references section
        for pattern in references_patterns:
            if pattern in report:
                parts = report.split(pattern, 1)
                if len(parts) == 2:
                    main_content = parts[0].strip()
                    references_section = pattern + parts[1]
                    break
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": f"""You are a professional financial translator specializing in institutional market research. Translate this market newsletter to {language_map[target_language]} while following these CRITICAL rules:

TRANSLATION REQUIREMENTS:
1. PRESERVE all company names in English (Apple, Microsoft, Alibaba, Tesla, etc.)
2. PRESERVE all market index names in English (S&P 500, NASDAQ, Hang Seng, Nikkei 225, etc.)
3. PRESERVE all currency symbols and financial amounts exactly (USD, $, %, etc.)
4. PRESERVE all percentage values and numerical data exactly as written
5. PRESERVE all proper nouns and financial terminology that should remain in English for professional credibility
6. PRESERVE all markdown formatting (##, **, etc.) and structure

CONTENT GUIDELINES:
7. Translate narrative text, analysis, and commentary naturally
8. Maintain the sophisticated, institutional-grade tone and flow
9. Keep all section headers and emojis in the same positions
10. Ensure translated content reads naturally for native speakers while preserving financial accuracy

CRITICAL: Do NOT translate company names, market indices, financial instruments, or any proper nouns that are universally recognized in English within financial contexts. The goal is professional financial communication, not literal translation."""
                    },
                    {"role": "user", "content": main_content}
                ],
                max_tokens=3200,
                temperature=0.3
            )
            
            translated_content = response.choices[0].message.content.strip()
            
            # Combine translated content with original references
            if references_section:
                return translated_content + "\n\n" + references_section
            else:
                return translated_content
            
        except Exception as e:
            return f"Translation error: {str(e)}\n\n--- Original Report ---\n{report}"
    
    def _get_readable_name(self, symbol: str) -> str:
        """Convert symbol to readable name."""
        name_map = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones', 
            '^IXIC': 'NASDAQ',
            '^RUT': 'Russell 2000',
            '^FTSE': 'FTSE 100',
            '^GDAXI': 'DAX',
            '^FCHI': 'CAC 40',
            '^HSI': 'Hang Seng',
            '^N225': 'Nikkei 225',
            '^STOXX50E': 'Euro Stoxx 50',
            '^STI': 'Straits Times Index',
            '000001.SS': 'Shanghai Composite'
        }
        
        return name_map.get(symbol, symbol)
    
    def test_openai_connection(self) -> Dict:
        """Test OpenAI API connection."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": "Test connection for balanced newsletter generation."}
                ],
                max_tokens=10,
                temperature=0
            )
            
            return {
                'status': 'connected',
                'model': 'gpt-4o',
                'response': response.choices[0].message.content.strip(),
                'last_test': datetime.now().isoformat(),
                'approach': 'balanced_professional'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_test': datetime.now().isoformat()
            }
