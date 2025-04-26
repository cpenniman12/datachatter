import psycopg2
import json

def execute_sql(query, dbname="chatbot_semantic_db", user="cooperpenniman", 
                password="", host="localhost", port="5432"):
    """Executes a SQL query and returns the results"""
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    
    cur = conn.cursor()
    cur.execute(query)
    
    if query.strip().lower().startswith("select"):
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
    else:
        results = []
    
    cur.close()
    conn.close()
    return results

def get_schema():
    """Gets complete database schema information"""
    schema = {}
    
    # Get tables
    tables_query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name NOT IN ('table_metadata', 'column_metadata')
    ORDER BY table_name;
    """
    
    tables = execute_sql(tables_query)
    
    for table in tables:
        table_name = table['table_name']
        schema[table_name] = {
            'description': '',
            'columns': []
        }
        
        # Get columns
        columns_query = f"""
        SELECT 
            column_name, 
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = '{table_name}'
        ORDER BY ordinal_position;
        """
        
        columns = execute_sql(columns_query)
        
        # Get primary keys
        pk_query = f"""
        SELECT kc.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kc
        ON kc.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
        AND kc.table_name = '{table_name}'
        """
        
        pk_results = execute_sql(pk_query)
        primary_keys = [pk['column_name'] for pk in pk_results]
        
        # Get foreign keys
        fk_query = f"""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
        ON tc.constraint_name = ccu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND kcu.table_name = '{table_name}';
        """
        
        fk_results = execute_sql(fk_query)
        foreign_keys = {fk['column_name']: {'referenced_table': fk['foreign_table_name'], 
                                          'referenced_column': fk['foreign_column_name']} 
                      for fk in fk_results}
        
        # Get table description from metadata
        table_desc_query = f"""
        SELECT table_description 
        FROM table_metadata 
        WHERE table_name = '{table_name}';
        """
        table_desc_result = execute_sql(table_desc_query)
        
        if table_desc_result:
            schema[table_name]['description'] = table_desc_result[0]['table_description']
        
        # Process each column
        for column in columns:
            column_name = column['column_name']
            
            # Get column description
            col_desc_query = f"""
            SELECT column_description 
            FROM column_metadata 
            WHERE table_name = '{table_name}' 
            AND column_name = '{column_name}';
            """
            col_desc_result = execute_sql(col_desc_query)
            
            column_info = {
                'name': column_name,
                'type': column['data_type'],
                'nullable': column['is_nullable'],
                'is_primary_key': column_name in primary_keys,
                'foreign_key': foreign_keys.get(column_name),
                'description': col_desc_result[0]['column_description'] if col_desc_result else ''
            }
            
            schema[table_name]['columns'].append(column_info)
    
    return schema

def schema_to_prompt_format(schema):
    """Convert schema dict to a text format for Claude prompt"""
    lines = []
    
    for table_name, table_info in schema.items():
        lines.append(f"\n   {table_name} table:")
        
        if table_info['description']:
            lines.append(f"   Description: {table_info['description']}")
        
        if table_info['columns']:
            lines.append("   Columns:")
            
            for col in table_info['columns']:
                # Build column description with primary/foreign key info
                col_desc = f"      * {col['name']}"
                
                if col['is_primary_key']:
                    col_desc += " (PRIMARY KEY)"
                
                if col['foreign_key']:
                    fk = col['foreign_key']
                    col_desc += f" (FOREIGN KEY references {fk['referenced_table']}.{fk['referenced_column']})"
                
                if col['description']:
                    col_desc += f": {col['description']}"
                else:
                    col_desc += f" ({col['type']})"
                    
                lines.append(col_desc)
    
    return "\n".join(lines)

if __name__ == "__main__":
    schema = get_schema()
    prompt_text = schema_to_prompt_format(schema)
    
    with open('schema_prompt.txt', 'w') as f:
        f.write(prompt_text)
    
    print(f"Schema written to schema_prompt.txt")
    
    # Also save raw schema as JSON for future use
    with open('schema_raw.json', 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"Raw schema data written to schema_raw.json") 