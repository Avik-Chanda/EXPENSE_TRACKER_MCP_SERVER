import tempfile
from fastmcp import FastMCP
import os
import aiosqlite
from contextlib import asynccontextmanager

DB_PATH = os.path.join(tempfile.gettempdir(), "expenses.db")

def init_connection():
    return aiosqlite.connect(DB_PATH)

async def init_db():
    async with init_connection() as c:
        await c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              date TEXT NOT NULL,
              category TEXT NOT NULL,
              subcategory TEXT DEFAULT '',
              amount REAL NOT NULL,
              note TEXT DEFAULT ''
            )
        """)
        await c.commit()

@asynccontextmanager
async def lifespan(server: FastMCP):
    await init_db()
    yield

mcp = FastMCP("EXPENSE_TRACKER_MCP_SERVER", lifespan=lifespan)

@mcp.tool
async def list_expenses(start_date, end_date):
    """ List all the expenses within date range """

    async with init_connection() as c:
        query = " SELECT id, date, category, subcategory, amount, note FROM expenses WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]

        async with c.execute(query,params) as curr: 
            cols = [d[0] for d in curr.description]
            rows = await curr.fetchall()
            return [dict(zip(cols,r)) for r in rows]

@mcp.tool
async def add_expenses(date, amount, category, subcategory="", note=""):
    """ Add expenses to the expenses db """
    async with init_connection() as c:
        query = """ INSERT INTO expenses(date, category, subcategory, amount, note) VALUES (?,?,?,?,?)"""
        params = [date, category, subcategory, amount, note]

        curr = await c.execute(query,params)
        await c.commit()
        return {
            "status": "ok",
            "id": curr.lastrowid
        }

@mcp.tool
async def summarize_expenses(start_date ,end_date, category=None):
    """ Summarize Expenses """

    async with init_connection() as c:
        query = "select date, amount, category, subcategory, note from expenses where date between ? and ?"
        params = [start_date,end_date]

        if category:
            query += " and category = ?"
            params.append(category)

        query += " group by category order by category asc"
        async with c.execute(query,params) as curr:
            cols = [d[0] for d in curr.description]
            rows = await curr.fetchall()
            return [dict(zip(cols,r)) for r in rows]

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8080)





    
 


