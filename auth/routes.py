from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .schema import LoginRequest , LoginResponse, RegisterRequest, RegisterResponse
from .service import login_user
from database import db

router = APIRouter()

@router.post("/login")
async def login(data:LoginRequest):
    dbData=await db.users.find_one({"email": data.email})
    print("DB Data:", dbData)  # Debugging line to check the fetched user data
    if dbData is None or dbData["password"] != data.password:  
       raise HTTPException(status_code=404, detail="user not found")

    token = await login_user(data)  
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=str(dbData["_id"]),  # Convert ObjectId to stringdbData["_id"],
        email=dbData["email"],
        full_name=dbData["full_name"],
    )
@router.post("/register")
async def register(data:RegisterRequest):
    dbData=await db.users.find_one({"email": data.email})
    if dbData is not None:  
        return {"error": "User already exists"}
    dbData =await  db.users.insert_one({
        "email": data.email,
        "password": data.password,
        "full_name": data.full_name,
        "owned_items": [],
    })
    token = await login_user(data)
    return RegisterResponse(
        access_token=token,
        token_type="bearer",
        user_id=str(dbData.inserted_id),  # Use inserted_id for new user
        email=data.email,
        full_name=data.full_name,
        owned_items=[]  # New user has no items yet
    )
    
@router.get("/users")
def get_users():
    users = list(db.users.find())
    for user in users:
        user["_id"] = str(user["_id"])
    return users


