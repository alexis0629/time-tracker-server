from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import datetime

DB_NAME = "server_logs.db"
app = FastAPI()

# Define the data model
class WorkLog(BaseModel):
    user_id: str
    timestamp: datetime.datetime
    hours: float

# Set up the database
def setup_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp DATETIME,
            hours REAL
        )
    ''')
    conn.commit()
    conn.close()

setup_db()

@app.post("/log")
def receive_log(log: WorkLog):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            INSERT INTO logs (user_id, timestamp, hours)
            VALUES (?, ?, ?)
        ''', (log.user_id, log.timestamp, log.hours))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Log saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/{user_id}")
def get_user_logs(user_id: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM logs WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return {"user_id": user_id, "logs": rows}

@app.get("/total/{user_id}")
def get_total_hours(user_id: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT SUM(hours) FROM logs WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return {"user_id": user_id, "total_hours": result[0] or 0}
