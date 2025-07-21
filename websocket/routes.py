from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List
from datetime import datetime
from bson import ObjectId
from database import db
from items.schema import BidEntry

app = APIRouter()

active_connections: Dict[str, List[WebSocket]] = {}


async def connect_bidder(item_id: str, websocket: WebSocket):
    await websocket.accept()
    if item_id not in active_connections:
        active_connections[item_id] = []
    active_connections[item_id].append(websocket)
    print(f"WebSocket connected for item {item_id}, total: {len(active_connections[item_id])}")


async def disconnect_bidder(item_id: str, websocket: WebSocket):
    if item_id in active_connections and websocket in active_connections[item_id]:
        active_connections[item_id].remove(websocket)
        print(f"WebSocket disconnected for item {item_id}, remaining: {len(active_connections[item_id])}")


async def broadcast_bid(item_id: str, data: dict):
    for conn in active_connections.get(item_id, []):
        try:
            await conn.send_json(data)
        except Exception as e:
            print(f"Error sending message to client: {e}")


@app.websocket("/{item_id}")
async def websocket_endpoint(websocket: WebSocket, item_id: str):
    await connect_bidder(item_id, websocket)
    try:
        while True:
            bid_data = await websocket.receive_json()
            bid_amount = bid_data.get("bid")
            bidder = bid_data.get("bidder")

            # 1. Fetch latest item with full bid history
            item = await db.items.find_one({"_id": ObjectId(item_id)})

            if not item:
                await websocket.send_json({"error": "Item not found."})
                continue

            bid_history = item.get("bid_history", [])
            last_bid = bid_history[-1] if bid_history else None

            # 2. Prevent consecutive bids by same user
            if last_bid and last_bid.get("user_id") == bidder:
                await websocket.send_json({"error": "You cannot place two consecutive bids."})
                continue

            # 3. Validate bid amount
            current_bid = item.get("current_bid", 0)
            if bid_amount is None or bid_amount <= current_bid:
                await websocket.send_json({"error": "Bid must be higher than current bid."})
                continue

            # 4. Create BidEntry
            bid = BidEntry(
                user_id=bidder,
                bid_amount=bid_amount,
                timestamp=datetime.utcnow()
            )

            # 5. Update DB with new bid
            update_result = await db.items.update_one(
                {"_id": ObjectId(item_id)},
                {
                    "$set": {"current_bid": bid_amount},
                    "$push": {"bid_history": bid.dict()}
                }
            )

            # 6. Confirm update succeeded
            if update_result.modified_count == 0:
                await websocket.send_json({"error": "Failed to update bid in database."})
                continue

            # 7. Broadcast bid to all clients
            response = {
                "bid": bid_amount,
                "bidder": bidder,
                "timestamp": bid.timestamp.isoformat()
            }
            await broadcast_bid(item_id, response)

    except WebSocketDisconnect:
        await disconnect_bidder(item_id, websocket)
    except Exception as e:
        print(f"Unexpected WebSocket error: {e}")
        await disconnect_bidder(item_id, websocket)
