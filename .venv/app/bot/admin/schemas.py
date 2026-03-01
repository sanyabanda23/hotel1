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

class UserFilter(BaseModel):
    id: str

class SUpdatePhone(BaseModel):
    phone_nom: str

class SUpdateName(BaseModel):
    username: str

class SUpdateDescription(BaseModel):
    description: str

class SUpdateVk(BaseModel):
    vk_url: str

class SUpdateTg(BaseModel):
    tg_nik: str    
    
