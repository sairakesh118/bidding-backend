# jobs/finalize_auctions.py
from datetime import datetime
from pymongo import MongoClient
import pytz

client = MongoClient("mongodb://localhost:27017")
db = client["your_database"]  # replace with your actual DB name
auctions = db["auctions"]

def finalize_ended_auctions():
    now = datetime.now(pytz.utc)

    ended_auctions = auctions.find({
        "end_time": {"$lt": now},
        "status": "active"
    })

    for auction in ended_auctions:
        if not auction.get("bid_history"):
            continue

        last_bid = auction["bid_history"][-1]
        winner_id = last_bid["user_id"]
        final_bid = last_bid["bid_amount"]

        auctions.update_one(
            {"_id": auction["_id"]},
            {
                "$set": {
                    "status": "completed",
                    "owner": winner_id,
                    "final_bid": final_bid,
                    "updated_at": now
                }
            }
        )

        print(f"Auction {auction['_id']} finalized. Winner: {winner_id}, Bid: {final_bid}")
