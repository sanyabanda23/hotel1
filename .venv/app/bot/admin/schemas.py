from pydantic import BaseModel


class SNewPay(BaseModel):
    summ: int
    id_booking: int

class SCheckUser(BaseModel):
    phone_nom: int

class SCheckTgUser(BaseModel):
    tg_nik: str

class SCheckVkUser(BaseModel):
    vk_url: str
