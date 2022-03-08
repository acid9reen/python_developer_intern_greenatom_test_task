import datetime as dt

from pydantic import BaseModel


class ShowImageFile(BaseModel):
    filename: str
    registration_date_time: dt.datetime

    class Config():
        orm_mode = True


class ImageFile(BaseModel):
    request_code: int
    filename: str
    registration_date_time: dt.datetime

    class Config():
        orm_mode = True
