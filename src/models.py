from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Inbox(Base):
    __tablename__ = "inbox"

    request_code = Column(Integer)
    filename = Column(String, primary_key=True)
    registration_date_time = Column(DateTime)
