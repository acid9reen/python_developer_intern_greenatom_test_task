from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Inbox(Base):
    __tablename__ = "inbox"

    id = Column(Integer, primary_key=True)
    request_code = Column(String)
    filename = Column(String)
    registration_date_time = Column(DateTime)
