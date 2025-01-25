from flask import Flask, request, render_template, send_file
import sqlite3
import pandas as pd
from nltk.tokenize import word_tokenize
import nltk
import os

# Explicitly set the path to NLTK data
nltk.data.path.append(os.path.join(os.path.expanduser("~"), "nltk_data"))
nltk.download('punkt', download_dir=os.path.join(os.path.expanduser("~"), "nltk_data"))


app = Flask(__name__)

# Function to create the database and add sample data
def setup_database():
    conn = sqlite3.connect("sample.db")
    cursor = conn.cursor()
    # Create the table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary INTEGER
        )
    """)
    # Check if the table is empty before inserting data
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:  # If the table is empty
        cursor.executemany("""
            INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)
        """, [
            ("Alice", "HR", 50000),
            ("Bob", "IT", 70000),
            ("Charlie", "IT", 80000)
        ])
    conn.commit()
    conn.close()


# Function to convert natural language to SQL query
def text_to_sql(query):
    tokens = word_tokenize(query.lower())
    if "hr" in tokens and "department" in tokens:
        return "SELECT * FROM employees WHERE department = 'HR';"
    elif "it" in tokens and "department" in tokens:
        return "SELECT name, salary FROM employees WHERE department = 'IT';"
    elif "total" in tokens and "salary" in tokens:
        return "SELECT SUM(salary) FROM employees;"
    elif "how many" in query.lower() and "employees" in tokens:
        return "SELECT COUNT(*) FROM employees;"
    else:
        return None

# Function to execute the SQL query
def execute_query(sql):
    try:
        conn = sqlite3.connect("sample.db")
        conn.row_factory = sqlite3.Row  # Enables dictionary-like rows
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]  # Convert rows to dictionaries
    except sqlite3.Error as e:
        return f"Database error: {str(e)}"

# Route for the main web interface
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_query = request.form["query"]
        sql_query = text_to_sql(user_query)
        if sql_query:
            results = execute_query(sql_query)
        else:
            results = "Sorry, I couldn't understand your query."
        return render_template("index.html", query=user_query, results=results)
    return render_template("index.html")

# Route to download query results
@app.route("/download", methods=["POST"])
def download():
    sql_query = request.form["sql_query"]
    results = execute_query(sql_query)

    if results and not isinstance(results, str):
        # Convert results to a DataFrame
        df = pd.DataFrame(results)
        file_path = "query_results.csv"
        df.to_csv(file_path, index=False)
        return send_file(file_path, as_attachment=True)
    else:
        return "No results to download."

# Route to upload a database file
@app.route("/upload", methods=["POST"])
def upload_database():
    if "database" in request.files:
        file = request.files["database"]
        file.save("uploaded.db")
        return "Database uploaded successfully!"
    return "No file uploaded."

if __name__ == "__main__":
    setup_database()  # Set up the sample database
    app.run(debug=True)
