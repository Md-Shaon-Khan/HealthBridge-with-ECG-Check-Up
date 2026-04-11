import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://your_username:your_password@cluster.mongodb.net/healthbridge_db")
DB_NAME = "healthbridge_db"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

users_col = db["users"]
predictions_col = db["predictions"]
feedback_col = db["doctor_feedback"]
contact_col = db["contact_messages"]

async def init_db_indexes():
    await users_col.create_index("user_id", unique=True)
    await predictions_col.create_index([("user_id", 1), ("created_at", -1)])
    await feedback_col.create_index("patient_id")