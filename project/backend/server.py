from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# ✅ Tokenizer function
def tokenize_sql(query):
    keywords = {'select', 'from', 'where', 'insert', 'into', 'values', 'update', 'set', 'delete'}
    symbols = {',', ';', '(', ')', '*', '=', '<', '>', '!='}

    tokens = []
    words = re.findall(r'\w+|\*|<=|>=|!=|=|<|>|,|;|\(|\)', query)

    for word in words:
        if word.lower() in keywords:
            tokens.append({'type': 'KEYWORD', 'value': word})
        elif word in symbols:
            tokens.append({'type': 'SYMBOL', 'value': word})
        else:
            tokens.append({'type': 'IDENTIFIER', 'value': word})

    return tokens

# ✅ Improved Parse Tree Generator (Supports all queries)
def generate_parse_tree(query):
    tree = {"name": "SQL Query", "children": []}
    query_lower = query.strip().lower()

    if query_lower.startswith('select'):
        select_match = re.search(r'select\s+(.*?)\s+from', query, re.IGNORECASE)
        from_match = re.search(r'from\s+(\w+)', query, re.IGNORECASE)
        where_match = re.search(r'where\s+(.+)', query, re.IGNORECASE)

        if select_match:
            select_node = {"name": "SELECT", "children": []}
            columns = [col.strip() for col in select_match.group(1).split(',')]
            for col in columns:
                select_node["children"].append({"name": col})
            tree["children"].append(select_node)

        if from_match:
            from_node = {"name": "FROM", "children": [{"name": from_match.group(1)}]}
            tree["children"].append(from_node)

        if where_match:
            where_clause = where_match.group(1)
            where_node = {"name": "WHERE", "children": []}

            operators = re.findall(r'\s+(AND|OR)\s+', where_clause, flags=re.IGNORECASE)
            conditions = re.split(r'\s+AND\s+|\s+OR\s+', where_clause, flags=re.IGNORECASE)

            if operators:
                operator = operators[0].upper()
                operator_node = {"name": operator, "children": []}

                for cond in conditions:
                    operator_node["children"].append({"name": cond.strip()})

                where_node["children"].append(operator_node)
            else:
                where_node["children"].append({"name": where_clause.strip()})

            tree["children"].append(where_node)

    elif query_lower.startswith('insert'):
        insert_match = re.search(r'into\s+(\w+)', query, re.IGNORECASE)
        values_match = re.search(r'values\s*\((.*?)\)', query, re.IGNORECASE)

        if insert_match:
            insert_node = {"name": "INSERT INTO", "children": [{"name": insert_match.group(1)}]}
            tree["children"].append(insert_node)

        if values_match:
            values_node = {"name": "VALUES", "children": []}
            values = [val.strip() for val in values_match.group(1).split(',')]
            for val in values:
                values_node["children"].append({"name": val})
            tree["children"].append(values_node)

    elif query_lower.startswith('update'):
        update_match = re.search(r'update\s+(\w+)', query, re.IGNORECASE)
        set_match = re.search(r'set\s+(.*?)\s*(where|$)', query, re.IGNORECASE)
        where_match = re.search(r'where\s+(.+)', query, re.IGNORECASE)

        if update_match:
            update_node = {"name": "UPDATE", "children": [{"name": update_match.group(1)}]}
            tree["children"].append(update_node)

        if set_match:
            set_node = {"name": "SET", "children": []}
            assignments = [assign.strip() for assign in set_match.group(1).split(',')]
            for assign in assignments:
                set_node["children"].append({"name": assign})
            tree["children"].append(set_node)

        if where_match:
            where_node = {"name": "WHERE", "children": [{"name": where_match.group(1).strip()}]}
            tree["children"].append(where_node)

    elif query_lower.startswith('delete'):
        delete_match = re.search(r'from\s+(\w+)', query, re.IGNORECASE)
        where_match = re.search(r'where\s+(.+)', query, re.IGNORECASE)

        if delete_match:
            delete_node = {"name": "DELETE FROM", "children": [{"name": delete_match.group(1)}]}
            tree["children"].append(delete_node)

        if where_match:
            where_node = {"name": "WHERE", "children": [{"name": where_match.group(1).strip()}]}
            tree["children"].append(where_node)

    return tree

# ✅ SQL Execution Endpoint
@app.route('/execute', methods=['POST'])
def execute_query():
    data = request.get_json()
    query = data.get('query').strip()

    tokens = tokenize_sql(query)
    parse_tree = generate_parse_tree(query)

    try:
        query_type = query.split()[0].lower()
        if query_type not in ['select', 'insert', 'update', 'delete']:
            return jsonify({
                "status": "error",
                "message": "Only SELECT, INSERT, UPDATE, and DELETE queries are supported.",
                "tokens": tokens,
                "parse_tree": parse_tree
            })

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        semantic_result = semantic_check(query, cursor)
        if semantic_result != "OK":
            return jsonify({
                "status": "semantic_error",
                "message": semantic_result,
                "tokens": tokens,
                "parse_tree": parse_tree
            })

        icg = generate_intermediate_code(query)
        optimization_suggestion = optimize_query(query)

        if query_type == 'select':
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            conn.close()
            return jsonify({
                "status": "success",
                "data": result,
                "intermediate": icg,
                "optimization": optimization_suggestion,
                "tokens": tokens,
                "parse_tree": parse_tree
            })
        else:
            cursor.execute(query)
            conn.commit()
            conn.close()
            return jsonify({
                "status": "success",
                "message": f"{query_type.upper()} query executed successfully.",
                "intermediate": icg,
                "optimization": optimization_suggestion,
                "tokens": tokens,
                "parse_tree": parse_tree
            })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "tokens": tokens,
            "parse_tree": parse_tree
        })

# ✅ Semantic Check Function
def semantic_check(query, cursor):
    query_lower = query.strip().lower()

    if query_lower.startswith('insert'):
        table_match = re.search(r'insert\s+into\s+(\w+)', query, re.IGNORECASE)
    elif query_lower.startswith('update'):
        table_match = re.search(r'update\s+(\w+)', query, re.IGNORECASE)
    elif query_lower.startswith('delete'):
        table_match = re.search(r'from\s+(\w+)', query, re.IGNORECASE)
    else:
        table_match = re.search(r'from\s+(\w+)', query, re.IGNORECASE)

    if not table_match:
        return "Semantic Error: Table name not found."

    table_name = table_match.group(1)
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if cursor.fetchone() is None:
        return f"Semantic Error: Table '{table_name}' does not exist."

    if query_lower.startswith('select'):
        columns_match = re.search(r'select\s+(.+?)\s+from', query, re.IGNORECASE)
        if not columns_match:
            return "Semantic Error: Columns not found."

        columns_string = columns_match.group(1).strip()
        if columns_string == '*':
            return "OK"

        selected_columns = [col.strip() for col in columns_string.split(',')]
        cursor.execute(f"PRAGMA table_info({table_name})")
        table_columns = [row[1] for row in cursor.fetchall()]

        for col in selected_columns:
            if col not in table_columns:
                return f"Semantic Error: Column '{col}' does not exist in table '{table_name}'."

    return "OK"

# ✅ Intermediate Code Generation
def generate_intermediate_code(query):
    query_lower = query.strip().lower()

    if query_lower.startswith('insert'):
        table_match = re.search(r'into\s+(\w+)', query, re.IGNORECASE)
        values_match = re.search(r'values\s*\((.*?)\)', query, re.IGNORECASE)

        if not table_match or not values_match:
            return "Invalid INSERT query structure for Intermediate Code."

        table_name = table_match.group(1)
        values = values_match.group(1).strip()

        return f"WRITE {table_name}\nVALUES {values}"

    elif query_lower.startswith('update'):
        table_match = re.search(r'update\s+(\w+)', query, re.IGNORECASE)
        set_match = re.search(r'set\s+(.*?)\s*(where|$)', query, re.IGNORECASE)

        if not table_match or not set_match:
            return "Invalid UPDATE query structure for Intermediate Code."

        table_name = table_match.group(1)
        set_values = set_match.group(1).strip()

        return f"UPDATE {table_name}\nSET {set_values}"

    elif query_lower.startswith('delete'):
        table_match = re.search(r'from\s+(\w+)', query, re.IGNORECASE)

        if not table_match:
            return "Invalid DELETE query structure for Intermediate Code."

        table_name = table_match.group(1)

        return f"DELETE FROM {table_name}"

    # SELECT Query
    table_match = re.search(r'from\s+(\w+)', query, re.IGNORECASE)
    columns_match = re.search(r'select\s+(.+?)\s+from', query, re.IGNORECASE)

    if not table_match or not columns_match:
        return "Invalid SELECT query structure for Intermediate Code."

    table_name = table_match.group(1)
    columns_string = columns_match.group(1).strip()

    if columns_string == '*':
        projection = "ALL COLUMNS"
    else:
        projection = columns_string

    return f"READ {table_name}\nPROJECT {projection}"

# ✅ Query Optimization
def optimize_query(query):
    suggestions = []
    query_lower = query.strip().lower()

    if query_lower.startswith('select'):
        if re.search(r'where\s+1\s*=\s*1', query, re.IGNORECASE):
            suggestions.append("Unnecessary condition 'WHERE 1=1' detected. Consider removing it.")

        if re.search(r'select\s+\*\s+from', query, re.IGNORECASE):
            suggestions.append("Using 'SELECT *' can slow down queries. Consider selecting specific columns.")

    elif query_lower.startswith('insert'):
        if not re.search(r'values\s*\(.*\)', query, re.IGNORECASE):
            suggestions.append("INSERT query missing VALUES clause.")

    elif query_lower.startswith('update'):
        if not re.search(r'set\s+.*', query, re.IGNORECASE):
            suggestions.append("UPDATE query missing SET clause.")

    elif query_lower.startswith('delete'):
        if not re.search(r'where\s+', query, re.IGNORECASE):
            suggestions.append("Consider adding WHERE clause to DELETE to avoid deleting all rows.")

    if not suggestions:
        return "Query is well-optimized."
    else:
        return '\n'.join(suggestions)

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
