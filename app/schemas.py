from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# -----------------------------------------
# User schemas
# -----------------------------------------
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str  # plaintext, backend zamieni w password_hash

class UserRead(UserBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# -----------------------------------------
# Gift schemas
# -----------------------------------------
class GiftBase(BaseModel):
    name: str
    description: Optional[str] = None
    est_price: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None

class GiftCreate(GiftBase):
    owner_id: int

class GiftRead(GiftBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

    class Config:
        from_attributes: True

# -----------------------------------------
# Friendship schemas
# -----------------------------------------
class FriendshipBase(BaseModel):
    user_id: int
    friend_id: int

class FriendshipCreate(FriendshipBase):
    pass

class FriendshipRead(FriendshipBase):
    id: int

    class Config:
        from_attributes: True

# -----------------------------------------
# Reservation schemas
# -----------------------------------------
class ReservationBase(BaseModel):
    reserved_by: int

class ReservationCreate(ReservationBase):
    gift_id: int

class ReservationRead(ReservationBase):
    gift_id: int
    reserved_at: datetime

    class Config:
        from_attributes: True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None

class UserLogin(BaseModel):
    email: str
    password: str