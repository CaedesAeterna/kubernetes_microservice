from fastapi import FastAPI, HTTPException
import mysql.connector
import os

app = FastAPI()

# Database configuration from environment variables
DB_HOST = os.environ.get("DB_HOST", "tiamat-db-0.tiamat-db.default.svc.cluster.local")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "rootpassword")
DB_NAME = os.environ.get("DB_NAME", "testdb")


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


@app.get("/data")
def read_data():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Could not connect to database")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM test_table;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows



@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI behind Nginx"}
 

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "message": "this is a v2 version of the app 2025-10-23"}


