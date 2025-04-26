from flask import Flask, render_template, request, jsonify
from Main import get_initial_response_from_claude, extract_sql_query, execute_sql, get_analysis_from_claude
from Main import extract_analysis, extract_suggestions, extract_product_recommendations, is_product_query
from Main import get_quick_product_info, get_product_info_for_specific_query
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
        # Check if it's a simple product query
        if is_product_query(user_message) and (user_message.lower() == "products" or 
                                              user_message.lower() == "what products do you have" or
                                              user_message.lower() == "show me your products" or
                                              user_message.lower() == "tell me about your products"):
            return jsonify({
                'response': get_quick_product_info(),
                'type': 'product_info'
            })
            
        # For specific product details that we can handle locally
        if is_product_query(user_message) and any(specific in user_message.lower() for specific in 
                                               ["techpro x1", "ultrabook pro", "ecobook", 
                                                "techguard", "productivity", "warranty", "compare"]):
            return jsonify({
                'response': get_product_info_for_specific_query(user_message),
                'type': 'product_info'
            })
        
        # Get response from Claude for all other queries
        initial_response = get_initial_response_from_claude(user_message)
        
        # Extract SQL query if present
        sql_query = extract_sql_query(initial_response)
        
        # Handle SQL query if present
        if sql_query:
            results = execute_sql(sql_query)
            
            # Get Claude's analysis of the results
            analysis_response = get_analysis_from_claude(user_message, sql_query, results)
            
            # Extract different parts of the analysis
            analysis = extract_analysis(analysis_response)
            suggestions = extract_suggestions(analysis_response)
            product_recommendations = extract_product_recommendations(analysis_response)
            
            return jsonify({
                'response': {
                    'sql_query': sql_query,
                    'analysis': analysis,
                    'suggestions': suggestions,
                    'product_recommendations': product_recommendations
                },
                'type': 'sql_analysis'
            })
        else:
            # For regular conversation or non-database questions
            return jsonify({
                'response': initial_response,
                'type': 'text'
            })
            
    except Exception as e:
        return jsonify({
            'response': "Oops! Something went wrong: " + str(e),
            'type': 'error'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 