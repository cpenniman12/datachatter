from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import os
from dotenv import load_dotenv
import psycopg2
import json
from datetime import datetime
import decimal
import anthropic
# import openai # Commented out as embeddings are not used
import numpy as np
import time # For simple streaming demo

# Load environment variables
load_dotenv()

# Initialize API clients
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# Using original old-style OpenAI API
# openai.api_key = os.getenv("OPENAI_API_KEY") # Commented out as embeddings are not used

# Cache for embeddings to avoid regenerating them
# embedding_cache = {} # Commented out as embeddings are not used

app = Flask(__name__)

# Import selected functions from Main.py
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

def execute_sql(query, dbname="chatbot_semantic_db", user="cooperpenniman", 
                password="", host="localhost", port="5432"):
    """
    Connects to the PostgreSQL database and executes the given query.
    If the query is a SELECT, fetches and returns the results.
    For other queries, commits the changes.
    """
    try:
        # Connect to PostgreSQL (quietly)
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        
        cur = conn.cursor()
        
        # Execute the query (silently)
        cur.execute(query)
        
        # If it's a SELECT statement, fetch results
        if query.strip().lower().startswith("select"):
            results = cur.fetchall()
            # Get column names
            colnames = [desc[0] for desc in cur.description]
            # Convert to list of dictionaries
            results = [dict(zip(colnames, row)) for row in results]
            # Only print result count for SELECT queries
            if len(results) > 0:
                print(f"Found {len(results)} results")
        else:
            results = []
        
        # Commit if needed and close the connection
        conn.commit()
        cur.close()
        conn.close()
        
        return results
    except Exception as e:
        # On error, print the query for debugging
        print(f"\nQuery that caused error: {query}")
        print(f"Database error: {str(e)}")
        return {"error": str(e)}

# def get_embedding(text, model="text-embedding-3-small"):
#     """
#     Get embedding from OpenAI API using the specified model using v0.x style.
#     Uses a cache to avoid regenerating embeddings for identical text.
#     """
#     # Check cache first
#     cache_key = f"{text}_{model}"
#     if cache_key in embedding_cache:
#         return embedding_cache[cache_key]
    
#     try:
#         text = text.replace("\\n", " ") # OpenAI recommends replacing newlines
#         # Use v0.x API style
#         response = openai.Embedding.create(input=[text], model=model)
#         embedding = response['data'][0]['embedding']
        
#         # Cache the result
#         embedding_cache[cache_key] = embedding
#         return embedding
#     except Exception as e:
#         print(f"Error generating OpenAI embedding: {str(e)}")
#         raise

def get_initial_response_from_claude(question):
    """
    Gets response from Claude using the Tools API for SQL generation.
    Uses tools to generate SQL when the user asks database-related questions.
    """
    # Hard-coded schema information extracted directly from the database
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
    
    # Use hardcoded schema instead of dynamic schema generation
    schema_description = hardcoded_schema
    
    # Define ONLY the SQL generation tool
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

    system_prompt = f"""You are a friendly and helpful AI assistant specializing in database querying.

Your role is to:
- Convert natural language questions into SQL queries based ONLY on the provided schema.
- ALWAYS call the generate_sql tool for all user questions.
- The database has the following tables and columns:
{schema_description}

IMPORTANT INSTRUCTIONS FOR DATABASE QUERIES:
1. ALWAYS use the generate_sql tool for ALL questions.
2. ONLY use the tables and columns listed in the schema description above. Do NOT invent tables or columns. Verify column names like primary/foreign keys from the list above.
3. When joining tables, ALWAYS use the appropriate primary and foreign keys:
   - Join tables using the exact foreign key relationships shown in the schema.
   - All foreign keys are explicitly marked with "(FOREIGN KEY references table.column)".
4. If the schema doesn't contain exactly what the user is asking for, use the most relevant tables and columns FROM THE PROVIDED SCHEMA.
5. Pay close attention to column names including their exact spelling and table prefixes.
6. Use JOINs, subqueries, and advanced SQL features when appropriate, but ensure all referenced tables/columns are in the provided schema.

IMPORTANT: Do not include any internal thinking or reasoning in your responses. Only provide the final output using the generate_sql tool."""

    try:
        print("\n🔄 Sending request to Claude (Streaming Enabled)...")
        user_message_content = question

        # Use stream=True
        with client.messages.stream(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            temperature=0.1,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message_content}],
            tools=tools,
            tool_choice={"type": "auto"}
        ) as stream:
            # Check the first event to see if it's a tool_use for SQL
            
            buffered_stream = [] # Store events while checking
            initial_event_processed = False
            is_sql_tool_call = False

            for event in stream:
                 # If we already decided it's text, break this initial check loop
                 if initial_event_processed and not is_sql_tool_call:
                      buffered_stream.append(event) # Buffer this event too
                      break

                 buffered_stream.append(event) # Buffer event before checking
                 
                 if event.type == 'message_start':
                     continue 

                 # Check for SQL Tool Use Start
                 if event.type == 'content_block_start' and event.content_block.type == 'tool_use':
                     if event.content_block.tool_use.name == "generate_sql":
                         print("✅ SQL generation tool detected by Claude.")
                         is_sql_tool_call = True
                         initial_event_processed = True
                         # Don't break yet, need to consume the tool input below
                     else:
                         print(f"⚠️ Unexpected tool started: {event.content_block.tool_use.name}")
                         # Treat as text response for now
                         is_sql_tool_call = False
                         initial_event_processed = True
                         break # Proceed to text streaming

                 # Check for Text Start
                 elif event.type == 'content_block_start' and event.content_block.type == 'text':
                     print("Claude starting direct text response (streaming)...")
                     is_sql_tool_call = False
                     initial_event_processed = True
                     break # Proceed to text streaming
                 
                 # Check for Text Delta (might come before block start sometimes)
                 elif event.type == "content_block_delta" and event.delta.type == "text_delta":
                      print("Claude starting direct text response (streaming)...")
                      is_sql_tool_call = False
                      initial_event_processed = True
                      break # Proceed to text streaming

                 # Handle SQL Tool Input Streaming (if it's an SQL call)
                 # This part assumes we are still in the loop ONLY if is_sql_tool_call is True
                 if is_sql_tool_call and event.type == 'content_block_stop':
                      # Once the tool block stops, get the final message to extract input
                      final_message = stream.get_final_message()
                      for block in final_message.content:
                          if block.type == 'tool_use' and block.name == 'generate_sql':
                              sql_query = block.input.get("sql_query", "")
                              print(f"\n🤖 Generated SQL Query:\n{sql_query}")
                              return f"<sql>{sql_query}</sql>"
                      # If tool wasn't found in final message (error)
                      print("Error: SQL Tool use detected but couldn't extract SQL from final message.")
                      return "Error: Failed to extract SQL query."

                 # Handle stream end or unexpected events during initial check
                 elif event.type == "message_stop":
                    print("Stream ended during initial check.")
                    # If it was supposed to be SQL but didn't finish, return error
                    if is_sql_tool_call:
                         return "Error: SQL Tool call incomplete."
                    # Otherwise, assume empty text response intended
                    is_sql_tool_call = False
                    initial_event_processed = True
                    break 
                 elif not initial_event_processed:
                     # If we haven't processed a meaningful start event yet, continue loop
                     continue
            
            # --- End of initial check loop ---

            # If SQL tool was called, we should have returned already.
            if is_sql_tool_call:
                 print("Error: Logic flaw, reached text streaming section after SQL tool call.")
                 return "Error: Internal logic error."

            # Consume the stream HERE, collect chunks, then return a new generator
            collected_chunks = []
            print("Collecting text chunks from stream...")
            try:
                # Process buffered events first
                for event in buffered_stream:
                    if event.type == "content_block_delta" and event.delta.type == "text_delta":
                        collected_chunks.append(event.delta.text)
                        print(event.delta.text, end="", flush=True)
                    elif event.type == "content_block_start" and event.content_block.type == "text":
                        collected_chunks.append(event.content_block.text)
                        print(event.content_block.text, end="", flush=True)
                
                # Process the rest of the stream
                for event in stream:
                    if event.type == "content_block_delta" and event.delta.type == "text_delta":
                        collected_chunks.append(event.delta.text)
                        print(event.delta.text, end="", flush=True)
                    elif event.type == "message_stop":
                        print("\nStream finished collecting.")
                        break
                    elif event.type == "error":
                        print(f"\nError during stream collection: {event.error.message}")
                        collected_chunks.append(f"\n[Error during streaming: {event.error.message}]")
                        break 
            except Exception as e:
                # Catch errors during the stream consumption phase
                print(f"\nException during stream collection: {str(e)}")
                import traceback
                traceback.print_exc()
                collected_chunks.append(f"\n[Error collecting response stream: {str(e)}]")

            # Define and return a generator that yields the collected chunks
            def chunk_generator(chunks):
                for chunk in chunks:
                    yield chunk
            
            print(f"Collected {len(collected_chunks)} chunks. Returning generator.")
            return chunk_generator(collected_chunks)

    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        import traceback
        print(traceback.format_exc())
        # Return an error string instead of a generator on initial setup error
        return f"Error generating response: {str(e)}"

def get_analysis_from_claude(question, sql_query, query_results):
    """
    Gets Claude's analysis of the SQL query results using tools.
    """
    # Define the analysis tools
    tools = [
        {
            "name": "analyze_data",
            "description": "Analyze query results and provide insights",
            "input_schema": {
                "type": "object",
                "properties": {
                    "analysis": {
                        "type": "string",
                        "description": "Analysis of the query results"
                    },
                    "suggestions": {
                        "type": "string",
                        "description": "Suggested follow-up queries"
                    }
                },
                "required": ["analysis"]
            }
        }
    ]
    
    system_prompt = """You are a friendly and helpful SQL analyst. 
    You will receive:
    1. The original user question
    2. The SQL query that was executed
    3. The results of that query
    
    Your task is to:
    1. Analyze the results in a clear, concise way
    2. Point out any interesting patterns or insights
    3. Answer the user's original question using the data
    4. Suggest any relevant follow-up queries they might be interested in
    
    Use the analyze_data tool to structure your response with:
    - Required analysis section
    - Optional suggestions for follow-up queries
    
    IMPORTANT: Do not include any internal thinking or reasoning in your responses. Only provide the final output."""

    # Format the query results for Claude
    formatted_results = json.dumps(query_results, indent=2, cls=DateTimeEncoder)
    
    message_content = f"""Original question: {question}
SQL Query executed: {sql_query}
Query Results: {formatted_results}

Please analyze these results and provide insights."""

    try:
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": message_content}
            ],
            tools=tools
        )
        
        # Check if Claude used the tool
        if message.content and len(message.content) > 0:
            for content in message.content:
                # Filter out any content containing thinking tags
                if content.type == 'text' and ("<thinking>" in content.text or "</thinking>" in content.text):
                    continue
                    
                if content.type == 'tool_use':
                    # Claude is requesting to use a tool - access the name directly from content
                    tool_name = content.name
                    tool_input = content.input
                    
                    if tool_name == "analyze_data":
                        # Extract the components from the tool call
                        analysis = tool_input.get("analysis", "")
                        suggestions = tool_input.get("suggestions", "")
                        
                        response = ""
                        if analysis:
                            response += f"<analysis>{analysis}</analysis>"
                        if suggestions:
                            response += f"<suggestions>{suggestions}</suggestions>"
                            
                        return response
        
        # If Claude didn't use the tool or used it incorrectly, return the text content
        response_text = ""
        if message.content:
            for content in message.content:
                if content.type == 'text':
                    # Remove thinking sections from the response
                    text = content.text
                    if "<thinking>" in text and "</thinking>" in text:
                        start = text.find("<thinking>")
                        end = text.find("</thinking>") + len("</thinking>")
                        text = text[:start] + text[end:]
                    response_text += text.strip()
                    
        if response_text:
            return response_text
        else:
            # Fallback if no text content
            return "I couldn't analyze the results. Please try again with a different query."
        
    except Exception as e:
        print(f"Error calling Claude API for analysis: {str(e)}")
        return f"Error analyzing results: {str(e)}"

def extract_sql_query(response):
    """
    Extracts SQL query from response if it exists.
    """
    if "<sql>" in response and "</sql>" in response:
        start = response.find("<sql>") + 5
        end = response.find("</sql>")
        return response[start:end].strip()
    return None

def extract_analysis(response):
    """
    Extracts analysis from response if it exists.
    """
    if "<analysis>" in response and "</analysis>" in response:
        start = response.find("<analysis>") + 10
        end = response.find("</analysis>")
        return response[start:end].strip()
    return None

def extract_suggestions(response):
    """
    Extracts suggestions from response if it exists.
    """
    if "<suggestions>" in response and "</suggestions>" in response:
        start = response.find("<suggestions>") + 13
        end = response.find("</suggestions>")
        return response[start:end].strip()
    return None

def simple_text_streamer(text, delay=0.01):
    """Generator to stream text word by word."""
    words = text.split(' ')
    for word in words:
        yield word + ' '
        time.sleep(delay) # Add small delay

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    response_data = {} # Not used directly for streaming response

    try:
        print("\nProcessing your request...")
        # This call now returns "<sql>...", an error string, or a generator function yielding collected chunks
        initial_response_or_gen_func = get_initial_response_from_claude(user_input)

        # Check if it returned SQL
        if isinstance(initial_response_or_gen_func, str) and initial_response_or_gen_func.startswith("<sql>"):
            sql_query = extract_sql_query(initial_response_or_gen_func)
            print("\n🔍 SQL query extracted.")
            print("\nQuerying database...")
            results = execute_sql(sql_query)

            if isinstance(results, dict) and 'error' in results:
                print(f"Database Error: {results['error']}")
                error_text = f"Database Error: {results['error']}"
                return Response(simple_text_streamer(error_text), mimetype='text/plain') 
            else:
                print("\nAnalyzing results...")
                analysis_response = get_analysis_from_claude(user_input, sql_query, results)
                analysis = extract_analysis(analysis_response)
                suggestions = extract_suggestions(analysis_response)

                response_string = ""
                if analysis: response_string += f"Analysis:\n{analysis}\n\n"
                if suggestions: response_string += f"Suggestions:\n{suggestions}\n\n"
                response_string = response_string.strip()

                print("\nStreaming analysis response...")
                # Use the new chunk_generator for analysis too?
                # For now, stick to simple_text_streamer for analysis part
                return Response(simple_text_streamer(response_string), mimetype='text/plain')

        # Check if it returned a generator function (direct text response from Claude)
        elif callable(initial_response_or_gen_func):
             print("\nStreaming direct text response from Claude (using collected chunks)...")
             # Directly use the returned generator (which yields collected chunks)
             chunk_generator = initial_response_or_gen_func 
             # Wrap it with stream_with_context 
             # Try removing stream_with_context as the generator might not need it
             return Response(chunk_generator, mimetype='text/plain')
        
        # Handle cases where it's an error string
        elif isinstance(initial_response_or_gen_func, str):
             print(f"\nReceived plain string response (likely error): {initial_response_or_gen_func}")
             # Use the simple_text_streamer for basic error strings
             # Also remove stream_with_context here for consistency
             return Response(simple_text_streamer(initial_response_or_gen_func), mimetype='text/plain')

        else:
             # Should not happen
             print(f"\nError: Unexpected response type from Claude processing: {type(initial_response_or_gen_func)}")
             error_text = "Error: Unexpected response type."
             return Response(simple_text_streamer(error_text), mimetype='text/plain')

    except Exception as e:
        print(f"Oops! An error occurred in chat route: {str(e)}")
        import traceback
        traceback.print_exc()
        # Stream the error message back
        error_text = "Oops! Something went wrong processing your request."
        return Response(simple_text_streamer(error_text), mimetype='text/plain')

if __name__ == '__main__':
    # Run with debug=False to test if debugger interferes with streaming
    app.run(host='0.0.0.0', port=5001, debug=False) 