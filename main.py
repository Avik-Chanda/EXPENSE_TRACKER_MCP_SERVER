import sqlite3
import tempfile
from fastmcp import FastMCP
import os

mcp = FastMCP("EXPENSE_TRACKER_MCP_SERVER")

DB_PATH = os.path.join(tempfile.gettempdir(), "expenses.db")

def init_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with init_connection() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              date TEXT NOT NULL,
              category TEXT NOT NULL,
              subcategory TEXT DEFAULT '',
              amount REAL NOT NULL,
              note TEXT DEFAULT ''
            )
        """)

init_db()

@mcp.tool
def list_expenses(start_date, end_date):
    """ List all the expenses within date range """

    with init_connection() as c:
        query = " SELECT id, date, category, subcategory, amount, note FROM expenses WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]

        curr = c.execute(query, params)
        cols = [d[0] for d in curr.description]
        return [dict(zip(cols,r)) for r in curr.fetchall()]

@mcp.tool
def add_expenses(date, amount, category, subcategory="", note=""):
    """ Add expenses to the expenses db """
    with init_connection() as c:
        query = """ INSERT INTO expenses(date, category, subcategory, amount, note) VALUES (?,?,?,?,?)"""
        params = [date, category, subcategory, amount, note]

        curr = c.execute(query,params)
        return {
            "status": "ok",
            "id": curr.lastrowid
        }

@mcp.tool
def summarize_expenses(start_date ,end_date, category=None):
    """ Summarize Expenses """

    with init_connection() as c:
        query = "select date, amount, category, subcategory, note from expenses where date between ? and ?"
        params = [start_date,end_date]

        if category:
            query += " and category = ?"
            params.append(category)

        query += " group by category order by category asc"

        curr = c.execute(query,params)

        cols = [d[0] for d in curr.description]
        return [dict(zip(cols,r)) for r in curr.fetchall()]

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8080)





    
 


