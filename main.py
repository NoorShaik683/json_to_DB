from flask import Flask, request, jsonify
import sqlite3
import json
import uuid
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


app = Flask(__name__)
CORS(app)

database_file_name = os.environ.get('DATABASE_FILE_NAME')


# Function to get SQLite column type based on Python data type
def get_column_type(value):
    if isinstance(value, int):
        return 'INTEGER'
    elif isinstance(value, float):
        return 'REAL'
    elif isinstance(value, str):
        return 'TEXT'
    else:
        return 'TEXT'  # Fallback to TEXT if the type is not recognized (e.g., datetime)



# Function to create the api_keys table if it doesn't exist
def create_api_keys_table():
    conn = sqlite3.connect(database_file_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY,
            api_key TEXT UNIQUE,
            read_permission BOOLEAN,
            write_permission BOOLEAN
        )
    ''')

    # Check if an admin key already exists
    cursor.execute("SELECT COUNT(*) FROM api_keys WHERE api_key = 'admin_123'")
    admin_exists = cursor.fetchone()[0]

    if not admin_exists:
        # Create an initial admin key with both read and write permissions
        admin_key = 'admin_123'
        cursor.execute(
            'INSERT INTO api_keys (api_key, read_permission, write_permission) VALUES (?, ?, ?)',
            (admin_key, True, True)
        )

    conn.commit()
    conn.close()


# Create the api_keys table on application startup
create_api_keys_table()



@app.route('/api/v1/json', methods=['POST'])
def store_json():
    api_key = request.headers.get('Authorization')

    if not validate_api_key(api_key, 'write'):
        return jsonify({"error": "You don't have access to perform this action"}), 403
    data = request.get_json()
    table_name = request.args.get('table_name')
    selected_keys = request.args.getlist('unique_keys')

    if not table_name:
        return jsonify({"error": "Table name is required"}), 400

    try:
        conn = sqlite3.connect(database_file_name)
        cursor = conn.cursor()

        # Check if the table already exists
        cursor.execute(f"PRAGMA table_info({table_name})")
        table_info = cursor.fetchall()

        if not table_info:
            # Create a table with dynamic columns based on JSON keys and their data types
            columns = ', '.join([f'{key} {get_column_type(data[0][key])}' for key in data[0].keys()])
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, {columns})')
            conn.commit()
        else:
            # Add missing columns to the existing table
            existing_columns = {info[1]: info[2] for info in table_info}
            for key, value in data[0].items():
                if key not in existing_columns:
                    cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {key} {get_column_type(value)}')
                    conn.commit()

        # Make the selected keys unique
        for key in selected_keys:
            cursor.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS {table_name}_{key}_unique ON {table_name}({key})')
            conn.commit()

        # Insert data into the dynamically created table
        for item in data:
            values = list(item.values())
            column_names = ", ".join(item.keys())
            placeholders = ", ".join(["?"] * len(item))

            cursor.execute(
                f'INSERT OR REPLACE INTO {table_name} ({column_names}) VALUES ({placeholders})',
                values
            )
            conn.commit()

        return jsonify({"message": f"JSON data stored in table '{table_name}' successfully"})
    except Exception as e:
        print(e)
        return jsonify({"error": f"Failed to store JSON data: {str(e)}"}), 500
    finally:
        conn.close()

# New API endpoint to get all table names
@app.route('/api/v1/tables', methods=['GET'])
def get_tables():
    try:
        conn = sqlite3.connect(database_file_name)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        return jsonify([table[0] for table in tables])
    except Exception as e:
        return jsonify({"error": f"Failed to get table names: {str(e)}"}), 500
    finally:
        conn.close()

# New API endpoint to get columns for a specific table
@app.route('/api/v1/columns/<table_name>', methods=['GET'])
def get_columns(table_name):
    try:
        conn = sqlite3.connect(database_file_name)
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute(f"PRAGMA table_info({table_name})")
        table_info = cursor.fetchall()

        if not table_info:
            return jsonify({"error": f"Table '{table_name}' does not exist"}), 404

        # Get column names
        columns = [info[1] for info in table_info]
        return jsonify(columns)
    except Exception as e:
        return jsonify({"error": f"Failed to get columns for table '{table_name}': {str(e)}"}), 500
    finally:
        conn.close()


@app.route('/api/v1/filter', methods=['GET'])
def filter_table():
    api_key = request.headers.get('Authorization')

    if not validate_api_key(api_key, 'read'):
        return jsonify({"error": "You don't have access to perform this action"}), 403
    table_name = request.args.get('table_name')
    column = request.args.get('column')
    search_string = request.args.get('search_string')

    if not table_name:
        return jsonify({"error": "Table name is required for filtering."}), 400
    if not column:
        return jsonify({"error": "Column name is required for filtering."}), 400
    if not search_string:
        return jsonify({"error": "Search string is required for filtering."}), 400

    try:
        conn = sqlite3.connect(database_file_name)
        cursor = conn.cursor()

        # Query the table for records matching the search criteria
        cursor.execute(f"SELECT * FROM {table_name} WHERE {column} LIKE ?", ('%' + search_string + '%',))
        records = cursor.fetchall()

        return jsonify(records)
    except Exception as e:
        return jsonify({"error": f"Failed to filter the table: {str(e)}"}), 500
    finally:
        conn.close()


# New API endpoint for advanced search with conditions
@app.route('/api/v1/filter_advanced', methods=['GET'])
def filter_table_advanced():
    api_key = request.headers.get('Authorization')
    if not validate_api_key(api_key, 'read'):
        return jsonify({"error": "You don't have access to perform this action"}), 403
    table_name = request.args.get('table_name')
    column = request.args.get('column')
    condition = request.args.get('condition')
    value = request.args.get('value')

    if not table_name:
        return jsonify({"error": "Table name is required for filtering."}), 400
    if not column:
        return jsonify({"error": "Column name is required for filtering."}), 400
    if not condition:
        return jsonify({"error": "Search condition is required for filtering."}), 400
    if not value:
        return jsonify({"error": "Search value is required for filtering."}), 400

    try:
        conn = sqlite3.connect(database_file_name)
        cursor = conn.cursor()

        # Query the table based on the search condition
        if condition == "Equal to":
            cursor.execute(f"SELECT * FROM {table_name} WHERE {column} = ?", (value,))
        elif condition == "Greater than":
            cursor.execute(f"SELECT * FROM {table_name} WHERE {column} > ?", (value,))
        elif condition == "Less than":
            cursor.execute(f"SELECT * FROM {table_name} WHERE {column} < ?", (value,))
        elif condition =="Greater than or Equal to":
            cursor.execute(f"SELECT * FROM {table_name} WHERE {column} >= ?", (value,))
        elif condition =="Less than or Equal to":
            cursor.execute(f"SELECT * FROM {table_name} WHERE {column} <= ?", (value,))
        elif condition == "Not Equal to":
            cursor.execute(f"SELECT * FROM {table_name} WHERE {column} != ?", (value,))
        
        else:
            return jsonify({"error": f"Invalid search condition: {condition}"}), 400

        records = cursor.fetchall()

        return jsonify(records)
    except Exception as e:
        return jsonify({"error": f"Failed to filter the table: {str(e)}"}), 500
    finally:
        conn.close()



# New API endpoint for generating API keys
@app.route('/api/v1/generate_api_key', methods=['POST'])
def generate_api_key():
    try:
        data = request.get_json()
        permissions = data.get('permissions', [])

        if 'read' not in permissions and 'write' not in permissions:
            return jsonify({"error": "Invalid permissions. Choose 'read', 'write', or both."}), 400

        # Generate a unique API key
        api_key = str(uuid.uuid4())

        # Store the API key and permissions in the database
        conn = sqlite3.connect(database_file_name)
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO api_keys (api_key, read_permission, write_permission) VALUES (?, ?, ?)',
            (api_key, 'read' in permissions, 'write' in permissions)
        )
        conn.commit()

        return jsonify({"api_key": api_key, "permissions": permissions})
    except Exception as e:
        print(e)
        return jsonify({"error": f"Failed to generate API key: {str(e)}"}), 500
    finally:
        conn.close()

# Updated API endpoint for validating API key and permissions
def validate_api_key(api_key, permission):
    conn = sqlite3.connect(database_file_name)
    cursor = conn.cursor()

    # Use string formatting to include the column name dynamically
    query = f'SELECT * FROM api_keys WHERE api_key = ? AND {permission}_permission = 1'
    cursor.execute(query, (api_key,))

    result = cursor.fetchone()
    print("API KEY",api_key,"Result : ",result)

    conn.close()

    return result is not None


if __name__ == '__main__':
    app.run(debug=True)
