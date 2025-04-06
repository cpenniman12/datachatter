"""
Setup and Execution Instructions:

1. Environment Setup:
   - Ensure Python 3.6+ is installed.
   - It is recommended to use a virtual environment to manage dependencies.
   - Navigate to the script's directory: cd /Users/cooperpenniman/Downloads/
   - Create a virtual environment: python3 -m venv venv
   - Activate the virtual environment: source venv/bin/activate

2. Install Dependencies:
   - With the virtual environment active, install required packages:
     pip install psycopg2-binary anthropic python-dotenv numpy openai

3. Environment Variables:
   - Create a file named `.env` in the same directory as the script (/Users/cooperpenniman/Downloads/).
   - Add your API keys to the `.env` file:
     ANTHROPIC_API_KEY=your_actual_anthropic_key
     OPENAI_API_KEY=your_actual_openai_key

4. Database Setup:
   - Ensure PostgreSQL server is running.
   - The script connects to a database named 'chatbot_semantic_db' by default.
     Ensure this database exists: CREATE DATABASE chatbot_semantic_db; (if not already created)
   - Enable the pgvector extension in the database:
     Connect via psql: psql -d chatbot_semantic_db
     Run: CREATE EXTENSION IF NOT EXISTS vector;
   - The script expects tables 'table_metadata' and 'column_metadata' with specific
     structures, including a 'vector' type column for embeddings. Ensure these
     are created. (Note: This script does not create them automatically).

5. Running the Script:
   - Make sure your virtual environment is active (`source venv/bin/activate` from the Downloads directory).
   - Navigate to the script's directory (`/Users/cooperpenniman/Downloads/`).
   - Run the script using: python3 tooltest.py

6. Implementation Details:
   - The script uses OpenAI's embedding API to generate vector embeddings of schema metadata.
   - Claude 3 Opus is used via Anthropic's Tools API for SQL generation and result analysis.
   - Vector similarity search in Postgres with pgvector finds relevant schema elements.
   - Embeddings are cached in memory to improve performance for similar queries.
"""
import psycopg2
import json
from datetime import datetime
import anthropic
import os
from dotenv import load_dotenv
import numpy as np
import openai

# Load environment variables
load_dotenv()

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initialize OpenAI client (for embeddings)
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cache for embeddings to avoid regenerating them
embedding_cache = {}

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

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def get_embedding(text, model="text-embedding-3-small"):
    """
    Get embedding from OpenAI API using the specified model.
    Uses a cache to avoid regenerating embeddings for identical text.
    """
    # Check cache first
    cache_key = f"{text}_{model}"
    if cache_key in embedding_cache:
        # Silent cache hit - no need to print
        return embedding_cache[cache_key]
    
    try:
        text = text.replace("\\n", " ") # OpenAI recommends replacing newlines
        response = openai_client.embeddings.create(input=[text], model=model)
        embedding = response.data[0].embedding
        # The embedding is already a list of floats, no complex parsing needed.
        if len(embedding) != 1536:
             # This check might be less critical with a dedicated API, but good practice.
             raise ValueError(f"Expected 1536 dimensions from {model}, got {len(embedding)}")
        
        # Cache the result - silently
        embedding_cache[cache_key] = embedding
        return embedding
    except Exception as e:
        print(f"Error generating OpenAI embedding: {str(e)}")
        # Consider logging the specific text that caused the error if needed for debugging
        # print(f"Text causing error: {text}") 
        raise # Re-raise the exception to be caught by the calling function

def update_metadata_embeddings():
    """
    Update embeddings for all metadata entries
    """
    # Get all metadata entries without embeddings
    tables_query = "SELECT id, table_name, table_description FROM table_metadata WHERE embedding IS NULL;"
    columns_query = "SELECT id, table_name, column_name, column_description FROM column_metadata WHERE embedding IS NULL;"

    tables = execute_sql(tables_query)
    columns = execute_sql(columns_query)
    
    # Also query total counts for debugging purposes
    total_tables_query = "SELECT COUNT(*) as count FROM table_metadata;"
    total_columns_query = "SELECT COUNT(*) as count FROM column_metadata;"
    
    total_tables = execute_sql(total_tables_query)
    total_columns = execute_sql(total_columns_query)
    
    total_tables_count = total_tables[0]['count'] if total_tables else 0
    total_columns_count = total_columns[0]['count'] if total_columns else 0
    
    print(f"Database contains {total_tables_count} tables and {total_columns_count} columns total.")
    
    if len(tables) > 0 or len(columns) > 0:
        print(f"Found {len(tables)} tables and {len(columns)} columns needing embeddings.")
    
        # Update table embeddings
        for i, table in enumerate(tables):
            # Less verbose progress indication
            if i == 0 or (i+1) % 5 == 0 or i+1 == len(tables):
                print(f"Processing table {i+1}/{len(tables)}")
            
            text = f"Table: {table['table_name']}\nDescription: {table['table_description']}"
            try:
                embedding = get_embedding(text)
                # Use parameterized query to prevent SQL injection vulnerabilities
                update_query = """
                UPDATE table_metadata 
                SET embedding = %s::vector 
                WHERE id = %s;
                """
                # Note: execute_sql currently doesn't support parameters directly, 
                # this change anticipates potential future modification or highlights best practice.
                # For now, we still format the query, but keep the parameterization idea.
                formatted_query = f"""
                UPDATE table_metadata 
                SET embedding = array{embedding}::vector 
                WHERE id = {table['id']};
                """
                execute_sql(formatted_query)
            except Exception as e:
                print(f"Failed to update embedding for table {table['table_name']}: {str(e)}")
    
        # Update column embeddings
        for i, column in enumerate(columns):
            # Less verbose progress indication
            if i == 0 or (i+1) % 10 == 0 or i+1 == len(columns):
                print(f"Processing column {i+1}/{len(columns)}")
                
            text = f"Table: {column['table_name']}\nColumn: {column['column_name']}\nDescription: {column['column_description']}"
            try:
                embedding = get_embedding(text)
                # Use parameterized query ideally
                update_query = """
                UPDATE column_metadata 
                SET embedding = %s::vector 
                WHERE id = %s;
                """
                # Formatting for current execute_sql
                formatted_query = f"""
                UPDATE column_metadata 
                SET embedding = array{embedding}::vector 
                WHERE id = {column['id']};
                """
                execute_sql(formatted_query)
            except Exception as e:
                print(f"Failed to update embedding for column {column['table_name']}.{column['column_name']}: {str(e)}")
    else:
        # Output for debug
        print("All table and column embeddings are already present in the database.")
        
        # Query for available tables
        tables_list_query = """
        SELECT table_name, table_description 
        FROM table_metadata 
        ORDER BY table_name;
        """
        
        print("\nAvailable tables in the database:")
        tables_list = execute_sql(tables_list_query)
        for i, table in enumerate(tables_list, 1):
            print(f"  {i}. {table['table_name']}" + 
                  (f" - {table['table_description']}" if table.get('table_description') else ""))

def get_schema_metadata(search_query):
    """
    Gets relevant schema metadata based on the user's question using vector similarity
    Returns the top 10 most semantically similar columns and their tables, without a threshold
    """
    # Get embedding for search query
    print(f"\n🔍 Searching for schema metadata relevant to: '{search_query}'")
    
    try:
        query_embedding = get_embedding(search_query)
        print(f"✅ Generated search embedding with {len(query_embedding)} dimensions")
    except Exception as e:
        print(f"❌ Error generating embedding: {str(e)}")
        return []
    
    # This query will get the top 10 most similar columns
    query = """
    SELECT 
        object_type,
        table_name,
        column_name,
        description,
        similarity
    FROM (
        SELECT 
            'column' as object_type,
            table_name,
            column_name,
            column_description as description,
            1 - (embedding <=> array{query_embedding}::vector) as similarity
        FROM column_metadata
        UNION ALL
        SELECT 
            'table' as object_type,
            table_name,
            NULL as column_name,
            table_description as description,
            1 - (embedding <=> array{query_embedding}::vector) as similarity
        FROM table_metadata
    ) as combined
    ORDER BY similarity DESC
    LIMIT 10;
    """.replace("{query_embedding}", str(query_embedding))
    
    print("Executing vector similarity search...")
    results = execute_sql(query)
    
    # Print similarity scores for debugging
    if results:
        print(f"Found {len(results)} schema matches with these similarity scores:")
        for i, item in enumerate(results, 1):
            similarity = item.get('similarity', 0) * 100  # Convert to percentage
            if item['object_type'] == 'table':
                print(f"  {i}. Table: {item['table_name']} - {similarity:.1f}% match")
            else:
                print(f"  {i}. Column: {item['table_name']}.{item['column_name']} - {similarity:.1f}% match")
    else:
        print("❌ No schema matches found in the vector similarity search")
    
    # If no results found (unlikely with this approach but good to have as fallback)
    if not results:
        print("\nFalling back to default schema tables...")
        query = """
        SELECT 
            'table' as object_type,
            table_name,
            NULL as column_name,
            table_description as description,
            1.0 as similarity
        FROM table_metadata
        ORDER BY table_name
        LIMIT 5;
        """
        tables = execute_sql(query)
        results = tables.copy()
        
        # Get 5 columns from each table (limit to avoid too many results)
        for table in tables:
            column_query = """
            SELECT 
                'column' as object_type,
                table_name,
                column_name,
                column_description as description,
                1.0 as similarity
            FROM column_metadata
            WHERE table_name = '{table_name}'
            ORDER BY column_name
            LIMIT 5;
            """.replace("{table_name}", table['table_name'])
            columns = execute_sql(column_query)
            results.extend(columns)
    
    return results

def get_initial_response_from_claude(question):
    """
    Gets response from Claude using the Tools API for SQL generation.
    Uses tools to generate SQL when the user asks database-related questions.
    """
    # Convert question to search terms by keeping only words 3+ characters
    search_terms = ' & '.join(word for word in question.lower().split() if len(word) >= 3)
    relevant_metadata = get_schema_metadata(search_terms)
    
    # Log the schema metadata being used for debugging
    print("\n📋 Debugging Schema Metadata:")
    if relevant_metadata:
        print(f"Found {len(relevant_metadata)} relevant schema items:")
        tables_found = set()
        for item in relevant_metadata:
            if item['object_type'] == 'table':
                tables_found.add(item['table_name'])
                print(f"  • Table: {item['table_name']}" + (f" - {item['description']}" if item.get('description') else ""))
            else:
                print(f"  • Column: {item['table_name']}.{item['column_name']}" + 
                      (f" - {item['description']}" if item.get('description') else ""))
        
        print(f"\nDistinct tables found: {', '.join(tables_found)}")
    else:
        print("⚠️ No relevant schema metadata found for this query!")
        print("This likely caused the NL2SQL tool to not be invoked.")
    
    # Format the metadata into a schema description
    schema_desc = []
    current_table = None
    
    for item in relevant_metadata:
        if item['object_type'] == 'table':
            if current_table != item['table_name']:
                schema_desc.append(f"\n   {item['table_name']} table:")
                if item['description']:
                    schema_desc.append(f"   Description: {item['description']}")
                current_table = item['table_name']
        else:  # column
            if current_table != item['table_name']:
                schema_desc.append(f"\n   {item['table_name']} table:")
                current_table = item['table_name']
            desc = f"      * {item['column_name']}"
            if item['description']:
                desc += f": {item['description']}"
            schema_desc.append(desc)

    schema_description = "\n".join(schema_desc)
    
    # If no tables or schema found, add a fallback schema
    if not schema_desc:
        print("\n⚠️ Using fallback schema due to no relevant tables found.")
        fallback_schema = """
   customers table:
   Description: Contains all customer information
      * customer_id: Unique identifier for each customer
      * name: Customer's full name
      * email: Customer's email address
      * phone: Customer's phone number
      * address: Customer's physical address
      * signup_date: Date the customer signed up
      * last_purchase_date: Date of the customer's most recent purchase
      
   products table:
   Description: Information about products sold by TechCorp
      * product_id: Unique identifier for each product
      * product_name: Name of the product
      * category: Category the product belongs to (laptop, software, etc.)
      * price: Current price of the product
      * release_date: Date the product was released
      * description: Detailed description of the product
      
   purchases table:
   Description: Record of all customer purchases
      * purchase_id: Unique identifier for each purchase
      * customer_id: ID of the customer who made the purchase
      * product_id: ID of the product that was purchased
      * purchase_date: Date the purchase was made
      * quantity: Number of items purchased
      * total_amount: Total amount of the purchase
      
   customer_support table:
   Description: Customer support tickets and interactions
      * ticket_id: Unique identifier for each support ticket
      * customer_id: ID of the customer who opened the ticket
      * product_id: ID of the product the ticket is about
      * issue_description: Description of the customer's issue
      * status: Current status of the ticket (open, in progress, resolved)
      * created_date: Date the ticket was created
      * resolved_date: Date the ticket was resolved
        """
        schema_description = fallback_schema

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

    system_prompt = f"""You are a friendly and helpful AI assistant for TechCorp, specializing in both product information and database querying.

Database Expert:
- Convert natural language questions into SQL queries about customer data
- When a user asks for customer/sales data, ALWAYS call the generate_sql tool
- The database has the following tables and columns:
{schema_description}

Product Expert:
- You can provide information about our product catalog
- We offer premium laptops (TechPro X1, UltraBook Pro), budget laptops (EcoBook), 
  software (TechGuard Pro, ProductivitySuite), and warranty options (Basic, Premium)

IMPORTANT INSTRUCTIONS FOR DATABASE QUERIES:
1. ALWAYS use the generate_sql tool if the question involves customer data, sales data, or database information
2. If the schema doesn't contain exactly what the user is asking for, use the most relevant tables and columns
3. Make an educated guess about relationships between tables based on column names
4. It's better to generate a SQL query that might not be perfect than to ask for clarification
5. Use JOINs, subqueries, and advanced SQL features when appropriate
6. For questions like "which customers use which products", always generate a SQL query using available tables

IMPORTANT: Do not include any internal thinking or reasoning in your responses. Only provide the final output."""

    # Check if the query has database keywords that should trigger SQL generation
    db_keywords = ["customers", "customer", "sales", "orders", "purchase", "data", 
                  "revenue", "transaction", "transactions", "database", "analytics",
                  "analysis", "statistics", "report", "metrics", "users", "usage"]
                  
    force_db_query = any(keyword in question.lower() for keyword in db_keywords) and not is_product_query(question)
    
    # Send the request to Claude with tools enabled
    try:
        print("\n🔄 Sending request to Claude...")
        if force_db_query:
            print("Forcing database query mode based on keywords detected.")
        
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": "IMPORTANT: If this question involves customer or database information, you MUST use the generate_sql tool: " + question if force_db_query else question}
            ],
            tools=tools
        )
        
        # Check if Claude used a tool
        tool_used = False
        if message.content and len(message.content) > 0:
            for content in message.content:
                # Filter out any content containing thinking tags
                if content.type == 'text' and ("<thinking>" in content.text or "</thinking>" in content.text):
                    continue
                
                if content.type == 'tool_use':
                    tool_used = True
                    print("✅ SQL generation tool was successfully invoked.")
                    # Claude is requesting to use the SQL tool
                    tool_name = content.name
                    tool_input = content.input
                    
                    if tool_name == "generate_sql":
                        # Extract the SQL query from the tool call
                        sql_query = tool_input.get("sql_query", "")
                        return f"<sql>{sql_query}</sql>"
        
        # If Claude didn't use the tool, log it
        if not tool_used:
            print("❌ Claude did not use the SQL tool on the first attempt.")
        
        # If Claude didn't use the tool and this looks like a database query, force another attempt
        if force_db_query and not tool_used:
            # Try again with a stronger instruction
            print("\n🔄 Making second attempt with stronger instruction...")
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": "GENERATE SQL QUERY FOR THIS QUESTION, DO NOT EXPLAIN OR ASK FOR CLARIFICATION: " + question}
                ],
                tools=tools
            )
            
            # Check for SQL tool use again
            second_attempt_tool_used = False
            if message.content and len(message.content) > 0:
                for content in message.content:
                    if content.type == 'tool_use' and content.name == "generate_sql":
                        second_attempt_tool_used = True
                        print("✅ SQL generation tool was successfully invoked on second attempt.")
                        sql_query = content.input.get("sql_query", "")
                        return f"<sql>{sql_query}</sql>"
            
            if not second_attempt_tool_used:
                print("❌ Claude did not use the SQL tool on the second attempt either.")
                print("Falling back to regular response.")
        
        # If Claude didn't use the tool, return the text content
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
            return "I couldn't generate a proper response. Please try rephrasing your question."
        
    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
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
                    },
                    "product_recommendations": {
                        "type": "string",
                        "description": "Product recommendations based on the data (optional)"
                    }
                },
                "required": ["analysis"]
            }
        }
    ]
    
    system_prompt = """You are a friendly and helpful TechCorp sales analyst. 
    You will receive:
    1. The original user question
    2. The SQL query that was executed
    3. The results of that query
    
    Your task is to:
    1. Analyze the results in a clear, sales-oriented way
    2. Point out any interesting patterns or insights relevant to our business
    3. Answer the user's original question using the data
    4. Suggest any relevant follow-up queries they might be interested in
    5. When appropriate, reference our product catalog to make product-specific recommendations
    
    Use the analyze_data tool to structure your response with:
    - Required analysis section
    - Optional suggestions for follow-up queries
    - Optional product recommendations based on the data
    
    IMPORTANT: Do not include any internal thinking or reasoning in your responses. Only provide the final output.
    
    Keep your tone professional and sales-focused while being informative."""

    # Format the query results for Claude
    formatted_results = json.dumps(query_results, indent=2, cls=DateTimeEncoder)
    
    message_content = f"""Original question: {question}
SQL Query executed: {sql_query}
Query Results: {formatted_results}

Please analyze these results and provide insights."""

    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
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
                        product_recommendations = tool_input.get("product_recommendations", "")
                        
                        response = ""
                        if analysis:
                            response += f"<analysis>{analysis}</analysis>"
                        if suggestions:
                            response += f"<suggestions>{suggestions}</suggestions>"
                        if product_recommendations:
                            response += f"<product_recommendations>{product_recommendations}</product_recommendations>"
                            
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

def extract_product_info(response):
    """
    Extracts product information from response if it exists.
    """
    if "<product_info>" in response and "</product_info>" in response:
        start = response.find("<product_info>") + 13
        end = response.find("</product_info>")
        return response[start:end].strip()
    return None

def extract_sales_message(response):
    """
    Extracts sales message from response if it exists.
    """
    if "<sales_message>" in response and "</sales_message>" in response:
        start = response.find("<sales_message>") + 15
        end = response.find("</sales_message>")
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

def extract_product_recommendations(response):
    """
    Extracts product recommendations from response if it exists.
    """
    if "<product_recommendations>" in response and "</product_recommendations>" in response:
        start = response.find("<product_recommendations>") + 20
        end = response.find("</product_recommendations>")
        return response[start:end].strip()
    return None

def is_product_query(question):
    """
    Quickly determines if a question is likely just asking about products.
    """
    product_keywords = [
        "product", "laptop", "computer", "techpro", "ultrabook", "ecobook",
        "software", "warranty", "price", "cost", "spec", "specification",
        "techguard", "productivitysuite", "features", "compare"
    ]
    
    question_lower = question.lower()
    for keyword in product_keywords:
        if keyword in question_lower:
            return True
    
    if "tell me about" in question_lower and "database" not in question_lower and "customer" not in question_lower:
        return True
    
    return False

def get_quick_product_info():
    """
    Returns a quick overview of our product catalog for immediate response.
    """
    return """Here is an overview of our main product offerings:

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

For more detailed information about a specific product, please ask!"""

def get_product_info_for_specific_query(query):
    """
    Returns detailed product information for specific product queries.
    """
    query_lower = query.lower()
    
    if "techpro x1" in query_lower:
        return """TechPro X1 - $1,299
- 14" 4K OLED display with HDR support and 100% DCI-P3 color gamut
- Intel i7-12700H (14 cores, up to 4.7GHz)
- 16GB DDR5 RAM (4800MHz)
- 1TB NVMe SSD with 7000MB/s read speeds
- NVIDIA RTX 3060 6GB dedicated graphics
- Battery: 12 hours of mixed usage
- Weight: 3.5 lbs / 1.59 kg
- Ports: 2x Thunderbolt 4, 1x USB-C, 2x USB-A, HDMI 2.1, SD card reader
- Backlit keyboard with 1.5mm key travel
- Wi-Fi 6E and Bluetooth 5.2
- Includes 1-year Basic warranty

Perfect for creative professionals, developers, and anyone who needs premium performance in a portable package."""

    elif "ultrabook pro" in query_lower:
        return """UltraBook Pro - $1,599
- 15.6" QHD (2560x1440) 165Hz display with anti-glare coating
- AMD Ryzen 9 5900HX (8 cores, up to 4.6GHz)
- 32GB DDR4 RAM (3200MHz)
- 2TB NVMe SSD in RAID 0 configuration
- NVIDIA RTX 3070 8GB dedicated graphics
- Battery: 10 hours of mixed usage
- Weight: 4.2 lbs / 1.9 kg
- Ports: 1x Thunderbolt 3, 2x USB-C, 3x USB-A, HDMI 2.1, Ethernet, 3.5mm audio
- RGB backlit keyboard with per-key lighting
- Wi-Fi 6 and Bluetooth 5.1
- Includes 1-year Basic warranty

Ideal for gamers, content creators, and power users who need desktop-class performance in a laptop."""

    elif "ecobook" in query_lower:
        return """EcoBook - $699
- 13.3" FHD IPS display (1920x1080)
- Intel i5-11300H (4 cores, up to 4.4GHz)
- 8GB DDR4 RAM (3200MHz)
- 512GB NVMe SSD
- Intel Iris Xe Graphics (integrated)
- Battery: 8 hours of mixed usage
- Weight: 2.9 lbs / 1.3 kg
- Ports: 1x Thunderbolt 4, 2x USB-A, HDMI, 3.5mm audio
- Backlit keyboard
- Wi-Fi 6 and Bluetooth 5.0
- Includes 1-year Basic warranty

Perfect for students, office work, and everyday computing with excellent value for money."""

    elif "techguard pro" in query_lower:
        return """TechGuard Pro - $129/year
- Complete antivirus protection with real-time scanning and heuristic analysis
- VPN with 200+ global servers in 50+ countries
- Password manager with secure vault and password generator
- 50GB secure cloud backup with end-to-end encryption
- Available for Windows, Mac, iOS, and Android (up to 5 devices)
- Parent controls and safe browsing tools
- Identity theft protection and dark web monitoring
- Regular automatic updates
- 24/7 technical support

Our most comprehensive security solution to keep your devices and data safe from threats."""

    elif "productivity" in query_lower:
        return """ProductivitySuite - $9.99/month
- Word processor with collaborative editing and advanced formatting
- Spreadsheet application with formulas, pivot tables, and data analysis tools
- Presentation software with templates and transition effects
- Email client with 100GB storage and advanced filtering
- Cloud storage: 2TB of secure online storage with file versioning
- Real-time collaboration with commenting and change tracking
- Available as web apps and desktop software for Windows and Mac
- Mobile apps for iOS and Android
- AI-powered features like grammar checking and data insights
- Regular feature updates and security patches

Everything you need to be productive at work, school, or home."""

    elif "warranty" in query_lower:
        return """WARRANTY OPTIONS:

Basic Warranty - Free with purchase
- 1-year limited hardware warranty covering manufacturing defects
- 90-day phone support for technical issues
- Access to online knowledge base and community forums
- Software updates for pre-installed applications

Premium Warranty - $199
- 3-year extended warranty with comprehensive coverage
- 24/7 priority support with dedicated technicians
- Accidental damage protection (up to 2 incidents)
- One-time battery replacement during warranty period
- Advanced exchange service with next-business-day shipping
- Annual hardware check-up and optimization
- Data recovery services in case of drive failure

The Premium Warranty is recommended for business users and anyone who relies heavily on their device."""
    
    elif "compare" in query_lower:
        if "laptop" in query_lower:
            return """LAPTOP COMPARISON:

TechPro X1 ($1,299) vs UltraBook Pro ($1,599) vs EcoBook ($699)

DISPLAY:
- TechPro X1: 14" 4K OLED (3840x2160)
- UltraBook Pro: 15.6" QHD (2560x1440) 165Hz
- EcoBook: 13.3" FHD IPS (1920x1080)

PROCESSOR:
- TechPro X1: Intel i7-12700H (14 cores)
- UltraBook Pro: AMD Ryzen 9 5900HX (8 cores)
- EcoBook: Intel i5-11300H (4 cores)

MEMORY:
- TechPro X1: 16GB DDR5 RAM
- UltraBook Pro: 32GB DDR4 RAM
- EcoBook: 8GB DDR4 RAM

STORAGE:
- TechPro X1: 1TB NVMe SSD
- UltraBook Pro: 2TB NVMe SSD (RAID 0)
- EcoBook: 512GB NVMe SSD

GRAPHICS:
- TechPro X1: NVIDIA RTX 3060 6GB
- UltraBook Pro: NVIDIA RTX 3070 8GB
- EcoBook: Intel Iris Xe Graphics (integrated)

BATTERY LIFE:
- TechPro X1: 12 hours
- UltraBook Pro: 10 hours
- EcoBook: 8 hours

WEIGHT:
- TechPro X1: 3.5 lbs
- UltraBook Pro: 4.2 lbs
- EcoBook: 2.9 lbs

BEST FOR:
- TechPro X1: Creative professionals, premium experience
- UltraBook Pro: Gaming, content creation, power users
- EcoBook: Students, office work, budget-conscious buyers"""
        else:
            return """PRODUCT COMPARISON:

Our product lineup is designed to meet different needs and budgets:

LAPTOPS:
- Premium: TechPro X1 ($1,299) and UltraBook Pro ($1,599)
- Budget: EcoBook ($699)

SOFTWARE:
- Security: TechGuard Pro ($129/year)
- Productivity: ProductivitySuite ($9.99/month)

WARRANTY OPTIONS:
- Basic: Free with purchase (1-year coverage)
- Premium: $199 (3-year coverage with additional benefits)

Each product is designed for specific use cases:
- TechPro X1: Thin and light premium experience with excellent display
- UltraBook Pro: Maximum performance for demanding tasks
- EcoBook: Affordable, portable computing for everyday tasks
- TechGuard Pro: Comprehensive security for all your devices
- ProductivitySuite: Complete office and productivity solution

All hardware products come with the Basic warranty, with the option to upgrade to Premium for extended coverage and benefits."""
    
    else:
        return get_quick_product_info()

def main():
    print("\nWelcome to TechCorp Assistant! I can help you with:")
    print("1. Customer and sales data analysis")
    print("2. Product information and specifications")
    print("Just let me know what you'd like to know about our products or customer data!")
    
    # Initialize embeddings for metadata (silently)
    print("\nInitializing semantic search capabilities...")
    try:
        update_metadata_embeddings()
        print("Semantic search initialized successfully!")
    except Exception as e:
        print(f"Warning: Could not initialize semantic search: {str(e)}")
        print("Falling back to basic schema...")
    
    while True:
        # Get user's input
        user_input = input("\nWhat would you like to know? (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            print("\nThank you for using TechCorp Assistant. Have a great day!")
            break
        
        try:
            # First, check if this is a simple, direct product query for immediate response
            if is_product_query(user_input) and (user_input.lower() == "products" or 
                                                user_input.lower() == "what products do you have" or
                                                user_input.lower() == "show me your products" or
                                                user_input.lower() == "tell me about your products"):
                print("\n📝 Product Information:")
                print(get_quick_product_info())
                continue
                
            # For specific product details that we can handle locally
            if is_product_query(user_input) and any(specific in user_input.lower() for specific in 
                                                  ["techpro x1", "ultrabook pro", "ecobook", 
                                                   "techguard", "productivity", "warranty", "compare"]):
                print("\n📝 Product Information:")
                print(get_product_info_for_specific_query(user_input))
                continue
            
            print("\nProcessing your request...")
            
            # Get response from Claude for all other queries
            initial_response = get_initial_response_from_claude(user_input)
            
            # Extract SQL query if present
            sql_query = extract_sql_query(initial_response)
            
            # Handle SQL query if present - indicate this might take longer
            if sql_query:
                print("\n🔍 Invoking natural language to SQL tool...")
                print("\nQuerying customer database...")
                results = execute_sql(sql_query)
                
                # Get Claude's analysis of the results
                print("\nAnalyzing results...")
                analysis_response = get_analysis_from_claude(user_input, sql_query, results)
                
                # Extract and display different parts of the analysis
                analysis = extract_analysis(analysis_response)
                suggestions = extract_suggestions(analysis_response)
                product_recommendations = extract_product_recommendations(analysis_response)
                
                if analysis:
                    print("\n📊 Analysis:")
                    print(analysis)
                
                if suggestions:
                    print("\n💡 Suggested follow-up queries:")
                    print(suggestions)
                
                if product_recommendations:
                    print("\n🌟 Product Recommendations:")
                    print(product_recommendations)
            else:
                # For regular conversation or non-database questions
                print("\n" + initial_response)
            
        except Exception as e:
            print(f"Oops! Something went wrong: {str(e)}")
            print(f"Error details: {str(e)}")

if __name__ == "__main__":
    main()
