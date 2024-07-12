from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True


class LicenseBase(BaseModel):
    client_name: str
    address: str
    date: date
    status: str
    licenseCategoryName: str


class LicenseCreate(LicenseBase):
    refno: int


class License(LicenseBase):
    refno: int

    class Config:
        orm_mode = True
