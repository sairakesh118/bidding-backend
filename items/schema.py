from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class BiddingItemCreate(BaseModel):
    name: str
    description: str
    starting_price: float
    end_time: datetime
    image_url: Optional[str] = None
    owner_id:Optional[str]=None # required at creation (user who lists the item)
    category: Optional[str] = None  # <-- Marked as optional for backward compatibility

class BiddingItemUpdateBid(BaseModel):
    bid_amount: float
    user_id: str  # bidder's ID (needed to track bids)

class BidEntry(BaseModel):
    user_id: str
    bid_amount: float
    timestamp: datetime

class BiddingItemOut(BaseModel):
    id: str
    name: str
    description: str
    starting_price: float
    category: Optional[str] = None  # <-- Marked as optional for backward compatibility
    current_bid: float
    end_time: datetime
    created_at: datetime
    updated_at: datetime
    bid_history: Optional[List[BidEntry]] = []
    owner_id: Optional[str] = None  # <-- Marked as optional
    winner_id: Optional[str] = None  # <-- Marked as optional
    image_url: Optional[str] = None  # <-- Marked as optional, for backward compatibility