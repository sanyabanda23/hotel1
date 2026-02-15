from datetime import date
from pydantic import BaseModel


class SNewUser(BaseModel):
    phone_nom: str
    name: str
    description: str
    

class SNewBooking(BaseModel):
    user_id: int
    room_id: int
    date_start: date
    date_end: date
    status: str
    cost: int

class UserPhoneFilter(BaseModel):
    phone_nom: str