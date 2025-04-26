# Anthropic SQL Tool

A conversational natural language to SQL query tool powered by Anthropic's Claude AI.

![Anthropic SQL Tool Screenshot](static/img/screenshot.png)

## Overview

This application allows users to ask questions about their database in natural language. The tool translates these questions into SQL queries, executes them, and presents the results in an intuitive chat interface. It also provides data visualization capabilities for query results.

## Features

- **Natural Language to SQL**: Ask questions in plain English and get SQL queries automatically generated
- **Conversational Interface**: Chat-like experience for interacting with your database
- **Query Execution**: Executes the generated SQL and displays results in a clean table format
- **Data Visualization**: Automatically visualizes query results when appropriate
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
AnthropicSQLTool/
├── static/
│   ├── css/
│   │   └── style.css        # Main stylesheet for the application
│   ├── js/
│   │   └── main.js          # Main JavaScript functionality
│   └── img/                 # Image assets
├── templates/
│   └── index.html           # Main HTML template
├── venv/                    # Python virtual environment
├── simplified_sql_app.py    # Main Flask application
├── requirements.txt         # Python dependencies
└── README_v2.md             # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Anthropic API key

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
   
   You can obtain an API key from the [Anthropic Console](https://console.anthropic.com/).

5. Optional: Configure database connections in `simplified_sql_app.py` if connecting to a real database.

### Running the Application

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
   ```

## Usage Guide

1. **Ask a Question**: Type your database-related question in the input field and press Enter or click the send button.

2. **View the SQL**: The application will generate a SQL query based on your question and display it.

3. **Browse Results**: If the query returns data, it will be displayed in a table format.

4. **Visualize Data**: For queries that return numerical data, a "Visualize Data" button will appear, allowing you to see a graphical representation of the results.

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Anthropic Claude API for natural language processing
- **Visualization**: Chart.js for data visualization

## Mock Database

The application currently uses mock data for demonstration purposes. It simulates queries on:

- Users
- Products
- Orders
- Companies
- Company financials

To connect to a real database, you would need to modify the `execute_sql()` function in `simplified_sql_app.py`.

## Customization

### Adding Custom Database Support

Modify the `execute_query` and related functions in `simplified_sql_app.py` to connect to your specific database.

### Styling

The application's appearance can be customized by modifying `static/css/style.css`.

## Troubleshooting

- **API Key Issues**: Ensure your Anthropic API key is correctly set in the `.env` file
- **Database Connection**: Check database connection strings if connecting to a real database
- **Port Conflicts**: If port 5000 is in use, modify the port in the Flask app configuration

## License

[MIT License](LICENSE)

## Acknowledgements

- Anthropic for providing the Claude API
- Flask for the web framework
- Chart.js for data visualization capabilities

## Data Visualization

The Anthropic SQL Tool provides powerful data visualization capabilities:

1. **Automatic Detection**: The system automatically analyzes query results to determine if they can be visualized
2. **One-Click Visualization**: Simply click the "Visualize Data" button that appears after a suitable query
3. **AI-Powered Chart Generation**: Claude AI determines the most appropriate visualization type based on your data
4. **Interactive Charts**: View charts in a modal popup with interactive features
5. **Multiple Chart Types**: Support for bar charts, line charts, pie charts, and more depending on the data structure

The visualization system:
- Identifies numeric columns in your query results
- Creates appropriate labels and scales
- Applies a consistent color scheme
- Generates responsive charts that work on all screen sizes

Example visualizations include:
- Company revenue comparisons
- Time-series data for stock prices
- Distribution of values across categories
- Aggregated metrics by different dimensions

## Interface Design

The Anthropic SQL Tool features a clean, modern interface designed for clarity and ease of use:

- **Minimalist Design**: Clean background with direct text display for easy reading
- **Message Threading**: Clear distinction between user questions and system responses
- **Syntax Highlighting**: SQL queries are displayed with proper formatting for readability
- **Loading Indicators**: Visual feedback when the system is processing
- **Responsive Tables**: Data tables that adjust to screen size and content
- **Modal Visualizations**: Charts appear in a non-disruptive modal overlay

The interface follows modern design principles:
- High contrast for readability
- Adequate spacing between elements
- Clear visual hierarchy
- Consistent color scheme with blue/purple accents
- Mobile-friendly responsive layout

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