from pydantic import BaseModel


class SNewPay(BaseModel):
    summ: int
    id_booking: int