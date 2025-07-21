import asyncio
from datetime import datetime,timezone
import pytz
from database import db as auctions_collection  # your MongoDB connection

async def finalize_ended_auctions():
    import pytz
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    print(f"[FINALIZE] Current UTC time: {now}")

    query = {
        "end_time": {"$gt": now},
        "winner_id": "pending"
    }

    cursor = auctions_collection.items.find(query)
    docs = await cursor.to_list(length=None)  # async fetch all documents

    print(f"docs: {docs}")  # Now you will see the documents printed correctly

    if not docs:
        print("[FINALIZE] No auctions found to finalize.")
        return

    for auction in docs:
        print(f"[FINALIZE] Found auction: {auction['_id']}")

        bid_history = auction.get("bid_history", [])
        if not bid_history:
            print(f"[FINALIZE] Auction {auction['_id']} ended with no bids.")
            continue

        last_bid = bid_history[-1]
        winner_id = last_bid["user_id"]
        final_bid = last_bid["bid_amount"]

        await auctions_collection.items.update_one(
            {"_id": auction["_id"]},
            {
                "$set": {
                    "winner_id": winner_id,
                    "final_bid": final_bid,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        print(f"[FINALIZE] Auction {auction['_id']} finalized. Winner: {winner_id}, Bid: {final_bid}")

