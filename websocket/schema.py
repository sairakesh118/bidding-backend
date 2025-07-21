from pydantic import BaseModel, Field

class BidMessage(BaseModel):
    bid: float = Field(..., gt=0, description="The bid amount (must be greater than 0)")
    bidder: str = Field(..., min_length=1, description="Name or ID of the bidder")
