from datetime import date
from pydantic import BaseModel


class SNewUser(BaseModel):
    phone_nom: str
    tg_nik: str
    vk_url: str
    username: str
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

class UserTgNikFilter(BaseModel):
    tg_nik: str

class UserVkUrlFilter(BaseModel):
    vk_url: str