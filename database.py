from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()  # Load variables from .env

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not set!")

client = AsyncIOMotorClient(MONGO_URI)
db = client["bidding"]
