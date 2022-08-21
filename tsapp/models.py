from sqlalchemy import Column, Integer, String

from .database import Base


class Stocks(Base):
    __tablename__ = "stocks"
    id = Column(Integer,primary_key=True)
    company_id = Column(Integer)
    date = Column(String)
    open = Column(String)
    high = Column(String)
    low = Column(String)
    close = Column(String)
    adjclose = Column(String)
    volume = Column(String)
