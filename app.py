from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import os
from services.benzinga_service import BenzingaService
from services.market_service import MarketService
from services.report_generator import ReportGenerator
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
benzinga_service = BenzingaService()
market_service = MarketService()
report_generator = ReportGenerator()

@app.route('/')
def index():
    """Main dashboard page with two tabs."""
    return render_template('index.html')

@app.route('/api/generate-recap', methods=['POST'])
def generate_recap():
    """Generate market recap using Benzinga news and OpenAI."""
    try:
        data = request.get_json()
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        language = data.get('language', 'English')
        
        # Get news articles from Benzinga
        articles = benzinga_service.get_articles_by_date_range(start_date, end_date)
        
        if not articles:
            return jsonify({
                'success': False,
                'error': 'No articles found for the selected date range'
            })
        
        # Get market data
        market_data = market_service.get_market_data_by_range(start_date, end_date)
        
        # Generate report
        report_content = report_generator.generate_market_report(
            market_data, articles, start_date, end_date, language
        )
        
        return jsonify({
            'success': True,
            'report': report_content,
            'articles_count': len(articles),
            'date_range': f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/market-data', methods=['POST'])
def get_market_data():
    """Get current market data for selected assets."""
    try:
        data = request.get_json()
        selected_stocks = data.get('stocks', [])
        selected_forex = data.get('forex', [])
        selected_indices = data.get('indices', [])
        
        # Get market data
        market_data = market_service.get_current_market_data(
            stocks=selected_stocks,
            forex=selected_forex,
            indices=selected_indices
        )
        
        return jsonify({
            'success': True,
            'data': market_data,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/available-assets')
def get_available_assets():
    """Get list of available stocks, forex, and indices."""
    return jsonify({
        'stocks': market_service.get_available_stocks(),
        'forex': market_service.get_available_forex(),
        'indices': market_service.get_available_indices()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)