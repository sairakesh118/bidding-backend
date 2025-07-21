from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from .schema import BiddingItemCreate, BiddingItemUpdateBid, BiddingItemOut, BidEntry
from database import db
from datetime import datetime
import pytz


app = APIRouter()

# Create a new auction item
from datetime import datetime
import pytz

@app.post("/", response_model=BiddingItemOut)
async def create_item(data: BiddingItemCreate):
    end_time = data.end_time

    # Ensure end_time is a UTC-aware datetime
    if not isinstance(end_time, datetime):
        end_time = datetime.fromisoformat(str(end_time))

    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=pytz.utc)
    else:
        end_time = end_time.astimezone(pytz.utc)
    print("data", data)  # Debugging line to check the processed end time
    item_data = {
        "name": data.name,
        "description": data.description,
        "starting_price": data.starting_price,
        "end_time": end_time,  # <--- Use processed UTC datetime here
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "current_bid": data.starting_price,
        "category": data.category,
        "bid_history": [],
        "owner_id": data.owner_id,
        "winner_id": "pending",
        "image_url": data.image_url if data.image_url else None,
    }
    result = await db.items.insert_one(item_data)
    item_data["id"] = str(result.inserted_id)
    return BiddingItemOut(**item_data)



# Get a single item by ID
@app.get("/{item_id}", response_model=BiddingItemOut)
async def get_item(item_id: str):
    try:
        object_id = ObjectId(item_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    
    item_data = await db.items.find_one({"_id": object_id})
    if not item_data:
        raise HTTPException(status_code=404, detail="Item not found")
    item_data["id"] = str(item_data["_id"])
    return BiddingItemOut(**item_data)

# Place a bid on an item
@app.put("/{item_id}", response_model=BiddingItemOut)
async def update_item(item_id: str, data: BiddingItemUpdateBid):
    try:
        object_id = ObjectId(item_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID")

    item = await db.items.find_one({"_id": object_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if data.bid_amount <= item["current_bid"]:
        raise HTTPException(status_code=400, detail="Bid amount must be higher than current bid")

    bid_entry = {
        "user_id": data.user_id,
        "bid_amount": data.bid_amount,
        "timestamp": datetime.utcnow()
    }

    await db.items.update_one(
        {"_id": object_id},
        {
            "$set": {
                "current_bid": data.bid_amount,
                "updated_at": datetime.utcnow()
            },
            "$push": {
                "bid_history": bid_entry
            }
        }
    )

    updated_item = await db.items.find_one({"_id": object_id})
    updated_item["id"] = str(updated_item["_id"])
    return BiddingItemOut(**updated_item)

# Delete an item
@app.delete("/{item_id}")
async def delete_item(item_id: str):
    try:
        object_id = ObjectId(item_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID")

    result = await db.items.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item deleted successfully"}

# List all items
@app.get("/", response_model=list[BiddingItemOut])
async def get_all_items():
    cursor = db.items.find()
    items = await cursor.to_list(length=100)
    for item in items:
        item["id"] = str(item["_id"])
        del item["_id"]
    return items

# Search items by name
@app.get("/search", response_model=list[BiddingItemOut])
async def search_items(query: str):
    cursor = db.items.find({"name": {"$regex": query, "$options": "i"}})
    items = await cursor.to_list(length=100)
    for item in items:
        item["id"] = str(item["_id"])
        del item["_id"]
    return items
