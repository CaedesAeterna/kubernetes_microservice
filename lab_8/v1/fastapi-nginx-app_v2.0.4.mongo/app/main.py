from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI()

# MongoDB configuration from environment variables
MONGODB_URL = os.environ.get(
    "MONGODB_URL", 
    "mongodb://mongo-0.mongo:27017,mongo-1.mongo:27017,mongo-2.mongo:27017/sampledb?replicaSet=rs0"
)

# Global MongoDB client and database
client = None
db = None

@app.on_event("startup")
async def startup_db_client():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client.sampledb
        # Test connection
        await client.admin.command('ping')
        print("Connected to MongoDB replica set")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
        print("Disconnected from MongoDB")

@app.get("/data")
async def read_data():
    if db is None:
        raise HTTPException(status_code=500, detail="Could not connect to database")
    
    try:
        # Get data from users collection (equivalent to test_table)
        cursor = db.users.find()
        rows = await cursor.to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for row in rows:
            row["_id"] = str(row["_id"])
        
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI behind Nginx"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "message": "this is a v2 version of the app 2025-10-23"}