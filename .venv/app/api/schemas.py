from pydantic import BaseModel


class SNewRoom(BaseModel):
    url_photo: str
    description: str