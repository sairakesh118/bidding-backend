from fastapi import APIRouter, HTTPException
from bson import ObjectId
from database import db

app = APIRouter()

# ✅ Helper to clean MongoDB documents
def clean_mongo_document(doc: dict) -> dict:
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc

# ✅ Get user profile by ID
@app.get("/{id}")
async def get_user_profile(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user_data = await db.users.find_one({"_id": object_id})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return clean_mongo_document(user_data)

# ✅ Get all auction items posted by a user (owner_id)
@app.get("/items/{id}")
async def get_user_items(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    items_data = await db.items.find({"owner_id": str(object_id)}).to_list(length=None)
    if not items_data:
        raise HTTPException(status_code=404, detail="No items found")

    return [clean_mongo_document(item) for item in items_data]

# ✅ Get all items where user won bids (winner_id)
@app.get("/bids/{name}")
async def get_user_bids(name: str):
    bids_data = await db.items.find({"winner_id": name}).to_list(length=None)
    if not bids_data:
        raise HTTPException(status_code=404, detail="No bids found")

    return [clean_mongo_document(item) for item in bids_data]
