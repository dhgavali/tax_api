from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class License(Base):
    __tablename__ = "license"

    refno = Column(Integer, primary_key=True)  # RefNo can hold up to 17 digits
    client_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    licenseCategoryName = Column(String, nullable=False)
