import json
import os
import sys
import re
import logging
import argparse
from datetime import datetime
import decimal
from flask import Flask, request, Response, jsonify, render_template, send_from_directory, redirect
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import Anthropic library and initialize client
try:
    import anthropic
    # Get API key from environment variable
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not found in environment variables.")
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your ANTHROPIC_API_KEY.")
        sys.exit(1)
    
    # Initialize Claude client
    client = anthropic.Anthropic(api_key=api_key)
except ImportError:
    logger.error("Anthropic library not found. Please install with: pip install anthropic")
    print("Error: Anthropic library not found. Please install with: pip install anthropic")
    sys.exit(1)

# Try to import database libraries (but don't fail if they're missing)
try:
    import psycopg2
    psycopg2_available = True
except ImportError:
    logger.warning("psycopg2 not found. PostgreSQL functionality will not be available.")
    psycopg2_available = False

try:
    import mysql.connector
    mysql_available = True
except ImportError:
    logger.warning("mysql-connector-python not found. MySQL functionality will be limited to mock data.")
    mysql_available = False

try:
    import sqlite3
    sqlite_available = True
except ImportError:
    logger.warning("sqlite3 not found. SQLite functionality will be limited to mock data.")
    sqlite_available = False

# Custom JSON encoder to handle datetime and decimal objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

def execute_sql(query, dbname=os.getenv("DB_NAME"), 
                user=os.getenv("DB_USER"), 
                password=os.getenv("DB_PASSWORD"), 
                host=os.getenv("DB_HOST"), 
                port=os.getenv("DB_PORT")):
    """
    Connects to the PostgreSQL database and executes the given query.
    Raises exceptions if the database connection fails or the query fails.
    """
    # Check if required connection details are present
    if not dbname:
        logger.error("DB_NAME environment variable not set.")
        raise ValueError("DB_NAME environment variable is required but not set.")
    if not user:
        logger.error("DB_USER environment variable not set.")
        raise ValueError("DB_USER environment variable is required but not set.")
    # Password can often be optional or handled differently, so we don't raise error if missing
    # if password is None: # os.getenv returns None if var doesn't exist and no default is set
    #    logger.warning("DB_PASSWORD environment variable not set.")
    if not host:
        logger.error("DB_HOST environment variable not set.")
        raise ValueError("DB_HOST environment variable is required but not set.")
    if not port:
        logger.error("DB_PORT environment variable not set.")
        raise ValueError("DB_PORT environment variable is required but not set.")

    # Check if we can use the real database
    if not psycopg2_available:
        logger.error("Cannot execute SQL: psycopg2 library is not installed.")
        raise ImportError("psycopg2 library is required but not installed. Please install it to connect to PostgreSQL.")

    conn = None
    cur = None
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password, # Will be None if not set, psycopg2 handles this
            host=host,
            port=port
        )
        logger.info("Connected to database '{}' on {}:{}".format(dbname, host, port))

        cur = conn.cursor()

        # Execute the query
        logger.info("Executing SQL query: {}".format(query))
        cur.execute(query)

        # If it's a SELECT statement, fetch results
        if query.strip().lower().startswith("select"):
            results = cur.fetchall()
            # Get column names
            colnames = [desc[0] for desc in cur.description]
            # Convert to list of dictionaries
            results = [dict(zip(colnames, row)) for row in results]
            logger.info("Query returned {} results.".format(len(results)))
        else:
            # For non-SELECT queries (INSERT, UPDATE, DELETE), report rows affected if available
            rowcount = cur.rowcount
            logger.info("Query executed successfully. Rows affected: {}".format(rowcount if rowcount != -1 else 'N/A'))
            results = [] # Return empty list for non-select queries

        # Commit changes if it wasn't a SELECT query
        if not query.strip().lower().startswith("select"):
            conn.commit()
            logger.info("Changes committed to the database.")

        return results

    except Exception as e:
        # Rollback in case of error during transaction
        if conn:
            conn.rollback()
        logger.error("Database error occurred for query: {}".format(query))
        logger.error("Error details: {}".format(str(e)))
        # Re-raise the exception to be handled by the caller
        raise e

    finally:
        # Ensure the cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()
            logger.info("Database connection closed.")

def get_sql_from_claude(question):
    """
    Gets SQL query from Claude using the Tools API.
    """
    # Hard-coded schema information
    hardcoded_schema = """
   analyst_estimates table:
   Description: Wall Street analyst recommendations and price targets
   Columns:
      * estimate_id (PRIMARY KEY): Primary key for analyst estimate records
      * company_id (FOREIGN KEY references companies.company_id): Foreign key linking to companies table
      * analyst_firm: Name of the firm providing the analysis
      * target_price: Analyst's 12-month price target
      * recommendation: Analyst's recommendation (Buy, Sell, Hold, etc.)
      * estimated_eps_next_quarter: Projected earnings per share for next quarter
      * estimated_revenue_next_quarter: Projected revenue for next quarter
      * estimate_date: Date when the estimate was published

   companies table:
   Description: Basic information about companies including sector, industry, and key details
   Columns:
      * company_id (PRIMARY KEY): Primary key and unique identifier for each company
      * ticker: Stock market ticker symbol
      * company_name: Full legal name of the company
      * sector: Economic sector the company operates in
      * industry: Specific industry within the sector
      * founded_date: Date when the company was founded
      * headquarters: Location of company headquarters
      * employee_count: Number of employees at the company
      * ceo_name: Name of the current CEO

   company_financials table:
   Description: Quarterly and annual financial data for companies including revenue and profits
   Columns:
      * financial_id (PRIMARY KEY): Primary key for financial records
      * company_id (FOREIGN KEY references companies.company_id): Foreign key linking to companies table
      * fiscal_year: Year of the financial reporting period
      * fiscal_quarter: Quarter of the financial reporting period (1-4)
      * revenue: Total sales during the reported period
      * gross_profit: Revenue minus cost of goods sold
      * operating_income: Profit from operations before interest and taxes
      * net_income: Profit after all expenses and taxes
      * eps: Earnings per share
      * total_assets: Total value of assets owned by the company
      * total_liabilities: Total debts and obligations owed by the company
      * cash_and_equivalents: Cash and liquid assets available to the company
      * report_date: Date when the financial report was published

   stock_prices table:
   Description: Daily stock price data for companies
   Columns:
      * price_id (PRIMARY KEY): Primary key for stock price records
      * company_id (FOREIGN KEY references companies.company_id): Foreign key linking to companies table
      * price_date: Date of the stock price information
      * open_price: Stock price at market open
      * high_price: Highest stock price during the trading day
      * low_price: Lowest stock price during the trading day
      * close_price: Stock closing price for the day
      * volume: Number of shares traded
      * adj_close: Adjusted closing price accounting for corporate actions

   supply_chain table:
   Description: Information about supplier relationships between companies
   Columns:
      * relationship_id (PRIMARY KEY): Primary key for supply chain relationship records
      * company_id (FOREIGN KEY references companies.company_id): Foreign key linking to companies table (the buyer)
      * supplier_id (FOREIGN KEY references companies.company_id): Foreign key linking to companies table (the supplier)
      * component: Component or service provided by the supplier
      * annual_value: Annual contract value in dollars
      * contract_start_date: Start date of the supplier contract
      * contract_end_date: End date of the supplier contract
      * risk_level: Risk assessment level of the supply relationship
    """
    
    # Define the SQL generation tool
    tools = [
        {
            "name": "generate_sql",
            "description": "Generate a SQL query based on the user's request and the database schema",
            "input_schema": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["sql_query"]
            }
        }
    ]

    system_prompt = """You are a database expert that converts natural language into SQL queries.

Database Expert:
- Convert natural language questions into SQL queries based ONLY on the provided schema.
- When a user asks for data, ALWAYS call the generate_sql tool.
- The database has the following tables and columns:
{}

IMPORTANT INSTRUCTIONS FOR DATABASE QUERIES:
1. ALWAYS use the generate_sql tool if the question involves data retrieval.
2. ONLY use the tables and columns listed in the schema description above. Do NOT invent tables or columns.
3. When joining tables, ALWAYS use the appropriate primary and foreign keys:
   - Join tables using the exact foreign key relationships shown in the schema.
   - All foreign keys are explicitly marked with "(FOREIGN KEY references table.column)".
4. If the schema doesn't contain exactly what the user is asking for, use the most relevant tables and columns FROM THE PROVIDED SCHEMA.
5. Pay close attention to column names including their exact spelling and table prefixes.
6. Use JOINs, subqueries, and advanced SQL features when appropriate, but ensure all referenced tables/columns are in the provided schema.""".format(hardcoded_schema)

    try:
        # Send the request to Claude with tools enabled
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            temperature=0.1,
            system=system_prompt,
            messages=[
                {"role": "user", "content": "Generate a SQL query for this request using only the provided schema: {}".format(question)}
            ],
            tools=tools,
            tool_choice={"type": "auto"}
        )
        
        # Extract SQL if Claude used the tool
        if message.content and len(message.content) > 0:
            for content_block in message.content:
                if content_block.type == 'tool_use' and content_block.name == "generate_sql":
                    sql_query = content_block.input.get("sql_query", "")
                    print("\nGenerated SQL Query:\n{}".format(sql_query))
                    return sql_query, None
        
        # If no tool was used, check for text response
        response_text = ""
        if message.content:
            for content_block in message.content:
                if content_block.type == 'text':
                    response_text += content_block.text.strip()
        
        return None, response_text
    
    except Exception as e:
        print("Error calling Claude API: {}".format(str(e)))
        return None, "Error generating SQL: {}".format(str(e))

# Initialize Flask app
app = Flask(__name__)

# System prompt for SQL generation
SYSTEM_PROMPT = """
You are an AI assistant that translates natural language questions into SQL queries.
Your task is to generate a SQL query based on the user's question.
Follow these rules:
1. Generate ONLY the SQL query, nothing else.
2. Use standard SQL syntax that works with PostgreSQL, MySQL, and SQLite.
3. If the question is unclear or doesn't seem to be about data that could be queried with SQL, respond with a message saying you can only answer questions that can be translated to SQL.
4. Make reasonable assumptions about table and column names based on the context of the question.
5. If the query is asking about people, assume there's a 'users' table with columns like 'id', 'name', 'email', 'created_at', etc.
6. If the query is about products, assume there's a 'products' table with columns like 'id', 'name', 'price', 'category', etc.
7. If the query is about sales or orders, assume there's an 'orders' table with columns like 'id', 'user_id', 'product_id', 'quantity', 'price', 'created_at', etc.
8. Use explicit JOIN syntax instead of WHERE clause joins.
9. Don't reference tables or columns that weren't mentioned or implied in the question.
"""

def get_visualization_from_claude(results):
    """Generate a visualization using Anthropic's Claude model."""
    try:
        logger.info("Requesting visualization from Claude API")
        
        # Convert results to JSON string for the prompt
        results_json = json.dumps(results[:20])  # Limit to 20 items to avoid token limits
        
        system_prompt = """
        You are an expert data visualization assistant. Your task is to create beautiful, interactive visualizations based on the data provided.
        
        Guidelines:
        1. Analyze the data structure and values to determine the most appropriate visualization type (bar chart, line chart, pie chart, scatter plot, etc.).
        2. Create clean, professional visualizations using Chart.js.
        3. Your response must contain valid HTML, CSS, and JavaScript that renders a visualization. It MUST include a <canvas> element with a unique ID.
        4. Include the Chart.js library via CDN WITHIN the returned HTML snippet.
        5. Make the visualization responsive and visually appealing with proper labels, titles, and colors.
        6. Return ONLY the HTML code needed to display the visualization, nothing else.
        7. For numerical data, consider appropriate scales and formats.
        8. Choose appropriate colors that are visually pleasing and accessible.
        9. IMPORTANT: Your entire response should be valid HTML that can be directly injected into a webpage.
        10. If the data has date/time values, consider using them for the x-axis.
        11. If there are multiple numeric columns, create a visualization that best represents their relationship.
        12. Add a clear title that describes what the visualization shows.
        13. CRITICAL JAVASCRIPT REQUIREMENT: All JavaScript code that initializes the Chart.js chart MUST be placed within its own <script> tag. This ENTIRE script block MUST be wrapped inside an event listener that waits for the DOM to be ready, like `document.addEventListener('DOMContentLoaded', function() { ... your chart code ... });` or placed at the very end of the HTML snippet you return. This ensures the canvas element exists before the script tries to use it.
        """
        
        user_prompt = """
        Please create a visualization for the following data:
        
        ```json
        {}
        ```
        
        Analyze this data and create the most appropriate chart using Chart.js. Return only the HTML code that renders the visualization.
        """.format(results_json)
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        # Extract the visualization HTML
        visualization_html = message.content[0].text
        
        # If the response is wrapped in code blocks, remove them
        visualization_html = re.sub(r'```html|```', '', visualization_html).strip()
        
        logger.info("Successfully generated visualization from Claude API")
        return visualization_html
    
    except Exception as e:
        logger.error("Error generating visualization: {}".format(str(e)))
        return "<div class='error'>Error generating visualization: {}</div>".format(str(e))

# Web interface routes
@app.route('/')
def index():
    """Render the chat interface."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/query', methods=['POST'])
def query():
    """API endpoint for processing questions and returning SQL query results."""
    data = request.json
    user_question = data.get('question', '')
    
    if not user_question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        logger.info("Processing question: {}".format(user_question))
        # Get SQL from Claude
        sql_query, text_response = get_sql_from_claude(user_question)
        
        # If SQL was generated, execute it
        if sql_query:
            try:
                results = execute_sql(sql_query)
                
                # Check if results contain an error message
                if isinstance(results, dict) and "error" in results:
                    logger.error("SQL execution error: {}".format(results['error']))
                    return jsonify({
                        "sql_query": sql_query,
                        "message": "The SQL query was generated but could not be executed: {}".format(results['error']),
                        "has_error": True
                    })
                
                # Check if we have empty results
                if not results or len(results) == 0:
                    logger.warning("SQL query produced no results: {}".format(sql_query))
                    return jsonify({
                        "sql_query": sql_query,
                        "message": "The query executed successfully but did not return any results.",
                        "results": [],
                        "empty_results": True
                    })
                
                # Log successful query execution
                result_count = len(results) if isinstance(results, list) else 0
                logger.info("Successfully executed SQL query with {} results".format(result_count))
                
                return jsonify({
                    "sql_query": sql_query,
                    "results": results,
                    "success": True
                })
            except Exception as e:
                logger.error("Error executing SQL: {}".format(str(e)))
                return jsonify({
                    "sql_query": sql_query,
                    "message": "I generated a SQL query, but there was an error executing it: {}".format(str(e)),
                    "has_error": True
                })
        else:
            # Return Claude's text response if no SQL was generated
            logger.warning("Could not generate SQL for question: {}".format(user_question))
            return jsonify({
                "message": text_response or "I couldn't generate a SQL query for your question. Could you please rephrase or provide more context?",
                "no_sql": True
            })
    except Exception as e:
        logger.error("Error processing query: {}".format(str(e)))
        return jsonify({
            "message": "Sorry, I encountered an error: {}".format(str(e)),
            "has_error": True
        }), 500

@app.route('/generate-visualization', methods=['POST'])
def generate_visualization():
    """API endpoint to generate visualizations from query results."""
    try:
        data = request.json
        results = data.get('results', [])
        
        if not results:
            logger.warning("No results provided for visualization")
            return jsonify({"error": "No results provided."}), 400
        
        # Check if the data is suitable for visualization
        if len(results) < 2:
            logger.warning("Not enough data points for visualization")
            return jsonify({
                "visualization_html": "<div class='error-message'>Not enough data points to create a meaningful visualization.</div>"
            })
        
        # Check if there's at least one numeric column
        has_numeric = False
        if results and isinstance(results[0], dict):
            for key, value in results[0].items():
                if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '', 1).isdigit()):
                    has_numeric = True
                    break
        
        if not has_numeric:
            logger.warning("No numeric columns for visualization")
            return jsonify({
                "visualization_html": "<div class='error-message'>No numeric data found. Visualization requires at least one column with numeric values.</div>"
            })
        
        # Get visualization HTML from Claude
        logger.info("Generating visualization for {} data points".format(len(results)))
        visualization_html = get_visualization_from_claude(results)
        
        return jsonify({
            "visualization_html": visualization_html
        })
    except Exception as e:
        logger.error("Error generating visualization: {}".format(str(e)))
        return jsonify({
            "visualization_html": "<div class='error-message'>Error generating visualization: {}</div>".format(str(e))
        }), 500

# Add a 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    # Handle static file 404 errors specially
    path = request.path
    if path.startswith('/static/'):
        if path.endswith('.js'):
            logger.warning("JavaScript file not found: {}".format(path))
            return "// JavaScript file not found: {}".format(path), 404, {'Content-Type': 'application/javascript'}
        elif path.endswith('.css'):
            logger.warning("CSS file not found: {}".format(path))
            return "/* CSS file not found: {} */".format(path), 404, {'Content-Type': 'text/css'}
    
    # For other 404 errors, redirect to home page
    logger.warning("Page not found: {}".format(path))
    return redirect('/')

def cli_mode():
    """Run the application in CLI mode."""
    print("\n===== SQL Chat Assistant (CLI Mode) =====")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        user_input = input("\nEnter your question: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        
        # Use get_sql_from_claude instead of generate_sql_query
        sql_query, text_response = get_sql_from_claude(user_input)
        
        if sql_query:
            print("\nGenerated SQL Query:")
            print("{}\n".format(sql_query))
            
            try:
                # Use execute_sql instead of execute_query
                results = execute_sql(sql_query)
                print("Query Results:")
                if results:
                    for row in results[:5]:  # Show only first 5 results
                        print(row)
                    if len(results) > 5:
                        print("... and {} more rows".format(len(results) - 5))
                else:
                     print("Query executed successfully, but returned no results or was not a SELECT statement.")

            except ImportError as ie:
                 print("Database Error: {}".format(str(ie)))
                 print("Please install the required database driver (e.g., pip install psycopg2-binary).")
            except Exception as e:
                print("Database Error: Failed to execute query: {}".format(str(e)))
        elif text_response:
            print("\nAssistant: {}".format(text_response))
        else:
            print("\nAssistant: Sorry, I couldn't generate a SQL query or understand your request.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SQL Chat Application')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    args = parser.parse_args()
    
    if args.cli:
        cli_mode()
    else:
        print("Starting SQL Chat Application...")
        print("Web interface available at: http://localhost:5001")
        print("For CLI mode, restart with: python simplified_sql_app.py --cli")
        app.run(host='0.0.0.0', port=5001) 