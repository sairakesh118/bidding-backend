from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserProfileResponse():
    id:str
    email: str
    fullname:str
