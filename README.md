# AnthropicSQLTool


TechCorp AI Assistant: Database & Product Query System
Overview
TechCorp AI Assistant is an advanced natural language interface for database querying and product information retrieval. This system combines semantic search, vector embeddings, and large language models to translate natural language questions into SQL queries, execute them, and provide insightful analysis of the results.
Table of Contents

System Architecture
How It Works
Key Components
Setup and Configuration
Adapting to Your Database
Troubleshooting
Advanced Features

System Architecture
The system combines multiple technologies to create a seamless query experience:
CopyUser Question → Semantic Search → Schema Selection → NL-to-SQL Conversion → 
SQL Execution → Result Analysis → User-Friendly Response
How It Works
1. Query Classification
When a user asks a question, the system first determines if it's a product query or a database query:

Product queries are handled immediately with pre-defined product information
Database queries go through the AI-powered SQL generation pipeline

2. Schema Metadata Retrieval
For database queries, the system:

Converts the user's question into a search vector using OpenAI embeddings
Performs a similarity search against table and column descriptions in PostgreSQL
Retrieves the most relevant schema elements to provide context for SQL generation
Uses fallback schema information if no relevant tables are found

3. Natural Language to SQL Conversion
The retrieved schema metadata is sent to Claude 3 Opus along with the user's question:

Claude analyzes the query and available schema
Using the Tools API, Claude generates appropriate SQL
If initially unsuccessful, the system makes a second attempt with stronger instructions
The generated SQL is extracted and executed against the database

4. Result Analysis and Presentation
Once results are obtained:

Results are sent back to Claude for analysis
Claude identifies key insights and patterns
The system structures the response with analysis, suggestions, and product recommendations
Information is presented to the user in clearly labeled sections

Key Components
1. Vector Database (PostgreSQL + pgvector)
The system uses pgvector extension in PostgreSQL to store and query vector embeddings of schema metadata, enabling semantic search of database structure.
2. Schema Metadata Storage
Two key tables store database structural information:

table_metadata: Information about tables and their purpose
column_metadata: Information about columns, their parent tables, and meanings

3. Embedding Generation
OpenAI's text-embedding-3-small model converts text descriptions into vector embeddings for:

Schema metadata (tables and columns)
User questions

4. AI-Powered SQL Generation
Claude 3 Opus generates SQL through the Anthropic Tools API, creating well-structured queries based on natural language questions and schema context.
5. Result Analysis
Claude analyzes query results to provide:

Business insights
Follow-up suggestions
Product recommendations based on data trends

Setup and Configuration
Prerequisites

Python 3.6+
PostgreSQL with pgvector extension
Anthropic API key (Claude 3 Opus)
OpenAI API key (for embeddings)

Environment Setup

Create a virtual environment
Install required packages: pip install psycopg2-binary anthropic python-dotenv numpy openai
Configure environment variables in .env file

Database Initialization

Create database: CREATE DATABASE your_semantic_db;
Enable pgvector: CREATE EXTENSION IF NOT EXISTS vector;
Create schema metadata tables (see below)
Populate with your database structure information
Generate embeddings for all metadata

Adapting to Your Database
Step 1: Create Metadata Tables
sqlCopyCREATE TABLE table_metadata (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    table_description TEXT,
    embedding vector(1536)
);

CREATE TABLE column_metadata (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    column_description TEXT,
    embedding vector(1536),
    UNIQUE(table_name, column_name)
);
Step 2: Populate Metadata
For each table in your database:

Add a record to table_metadata with a descriptive explanation
Add records to column_metadata for each column with clear descriptions
Focus on business meaning rather than technical details

Example:
sqlCopyINSERT INTO table_metadata (table_name, table_description) 
VALUES ('customers', 'Contains information about all registered customers including contact details and account status');

INSERT INTO column_metadata (table_name, column_name, column_description)
VALUES 
('customers', 'customer_id', 'Unique identifier for each customer'),
('customers', 'email', 'Primary contact email used for communications and account recovery'),
('customers', 'signup_date', 'Date when the customer first created their account');
Step 3: Generate Embeddings
Run the script with your populated metadata tables to generate embeddings:
pythonCopyupdate_metadata_embeddings()
Step 4: Customize System Prompts
Modify the system prompts in get_initial_response_from_claude() and get_analysis_from_claude() to:

Reflect your business domain
Incorporate your specific use cases
Adjust the tone and style to match your brand

Step 5: Test and Refine

Start with simple queries and verify SQL generation
Test complex queries that require joins and aggregations
Refine schema descriptions based on query performance
Add more detailed descriptions for frequently queried elements

Troubleshooting
SQL Generation Failures
If the system fails to generate SQL:

Check schema relevance: Ensure your query's keywords match schema descriptions
Improve metadata: Add more detailed descriptions to tables and columns
Add debugging prints: Use the verbose logging to see what schema is being provided
Add fallback schemas: Define standard patterns for common relationship types

Poor Query Results
If queries return unexpected results:

Review generated SQL: Check for logical errors in joins or conditions
Enhance schema descriptions: Add more details about relationships between tables
Add examples: Update column descriptions with example values for clarity

Advanced Features
Schema Caching
The system implements caching for:

Embeddings: Avoid regenerating the same embeddings
Schema metadata: Reuse relevant schema elements for similar queries

Forced Database Mode
For queries that should use the database but aren't being detected:

Keyword detection forces database query mode
Second attempt mechanism with stronger instructions

Enhanced Analysis
The Tools API provides structured output with:

Data analysis specific to the user's question
Suggested follow-up queries for deeper exploration
Product recommendations based on query results


By following this guide, you can adapt the TechCorp AI Assistant to your own database, creating a powerful natural language interface for data exploration and analysis. The combination of semantic search with AI-powered SQL generation creates an intuitive yet powerful system for accessing your data without SQL expertise.
