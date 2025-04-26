## Anthropic SQL Tool

A conversational natural language to SQL query tool powered by Anthropic's Claude AI.

![Anthropic SQL Tool Screenshot](static/img/screenshot.png)

## Overview

Dummy financial data is fed into claude alongside user question, claude generates sql, script executes sql, returns the results back to the user, and then gives the user an option to create a visual from the data. If the user decides to generate a visual, the dataframe gets sent to another instance of claude, which writes HTML/CSS/CS code for the visual. This code is then rendered and presented in the chat. 


###*****FUTURE ENHANCEMENTS! 

UI: 
-- suggested follow up questions 
-- columns can get cut off sometimes 
-- user should be able to expand table to see all rows 


DATA VISUALIZER: 
Includes necessary dependencies:
when claude generates visuals within the web app, it uses the following: 
   React and ReactDOM
   Recharts library
   Babel for JSX transpilation
   Tailwind CSS
This allows for more intricate visuals. the claude app will also often undergo a step to first analyze the data to better plan for the visual. I have a script with these enhancements (future_enhancement_to_visual), but was having trouble rendering the resulting code in my app. 

BACKEND: 
- connect to more data sources, maybe in the form of 'tools'. Perhaps the model has permission to pull from client portfolio, calendar, the web, etc, to pull in additional context if it sees fit. 
- if sql does not compile correctly, give the model a chance to rewrite it. 
- add more dummy data 
-- semantic search for data schema instead of hard coding it in the system prompt 



## Data being queried 

See insert metadata for a full list of columns/tables. These tables have been populated with the dummy data generated in the 'insert_tablename.sql' scripts


### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/AnthropicSQLTool.git
   cd AnthropicSQLTool
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   **Note**: If you encounter issues with `psycopg2` installation, you may use `psycopg2-binary` instead, or install the required PostgreSQL development libraries for your system.

4. Create a `.env` file in the root directory with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
   

5. connect your DB so that you can execute the query. To connect to a real database, you would need to modify the `execute_sql()` function in `simplified_sql_app.py`.

1. Start the Flask application:
   ```
   python simplified_sql_app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://localhost:5001
   ```

3. To run in CLI mode (for testing without web interface):
   ```
   python simplified_sql_app.py --cli
   


## Deployment

For production deployments, consider the following options:

### Using Gunicorn (Recommended for Production)

```bash
gunicorn -w 4 -b 0.0.0.0:5001 simplified_sql_app:app
```

Parameters:
- `-w 4`: Run 4 worker processes
- `-b 0.0.0.0:5001`: Bind to all interfaces on port 5001

### Docker Deployment

1. Create a Dockerfile in the project root:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=simplified_sql_app.py
ENV FLASK_ENV=production

EXPOSE 5001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "simplified_sql_app:app"]
```

2. Build and run the Docker container:

```bash
docker build -t anthropic-sql-tool .
docker run -p 5001:5001 -e ANTHROPIC_API_KEY=your_api_key_here anthropic-sql-tool
```

### Security Considerations

When deploying to production:
- Use environment variables for sensitive information
- Consider adding authentication for the web interface
- Set up HTTPS using a reverse proxy like Nginx
- Apply rate limiting to prevent API abuse 
