from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    try:
        # For demo purposes, we'll just return a static response
        if "products" in user_message.lower():
            return jsonify({
                'response': """Here is an overview of our main product offerings:

PREMIUM LAPTOPS:
- TechPro X1 ($1,299): 14" 4K OLED, Intel i7, 16GB RAM, 1TB SSD, NVIDIA RTX 3060
- UltraBook Pro ($1,599): 15.6" QHD 165Hz, AMD Ryzen 9, 32GB RAM, 2TB SSD, NVIDIA RTX 3070

BUDGET LAPTOPS:
- EcoBook ($699): 13.3" FHD IPS, Intel i5, 8GB RAM, 512GB SSD, Intel Iris Xe Graphics

SOFTWARE:
- TechGuard Pro ($129/year): Antivirus, VPN, password manager, 50GB backup
- ProductivitySuite ($9.99/month): Office suite with 2TB cloud storage

WARRANTY OPTIONS:
- Basic (Free): 1-year hardware warranty, 90-day phone support
- Premium ($199): 3-year extended warranty with accidental damage protection

For more detailed information about a specific product, please ask!""",
                'type': 'product_info'
            })
        
        elif "company" in user_message.lower() or "stock" in user_message.lower():
            # Mock SQL analysis response
            return jsonify({
                'response': {
                    'sql_query': "SELECT c.company_name, c.sector, MAX(s.close_price) as highest_price FROM companies c JOIN stock_prices s ON c.company_id = s.company_id GROUP BY c.company_name, c.sector ORDER BY highest_price DESC LIMIT 1;",
                    'analysis': "Based on the query results, Company ABCD in the Technology sector has the highest stock price at $972.45. This is significantly higher than the industry average of $415.30, indicating strong market performance.",
                    'suggestions': "You might want to explore:\n- How has this company's stock price changed over time?\n- What's the average stock price by industry sector?\n- Which companies have seen the highest growth in stock price?",
                    'product_recommendations': "Given the analysis of high-performing tech companies, our UltraBook Pro would be an excellent choice for professionals in the technology sector. Its high-performance specifications are designed for demanding tasks."
                },
                'type': 'sql_analysis'
            })
        
        else:
            # Generic response
            return jsonify({
                'response': "I'm a simplified demo version of the TechCorp Assistant. You can ask me about our products or company data. Try asking about our products or stock prices!",
                'type': 'text'
            })
            
    except Exception as e:
        return jsonify({
            'response': "Oops! Something went wrong: " + str(e),
            'type': 'error'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 