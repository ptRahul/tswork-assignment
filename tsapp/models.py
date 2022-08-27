from typing import Optional
from sqlalchemy import Column, Integer, String

from .database import Base
from pydantic import BaseModel


class Stocks(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer)
    company_name = Column(String)
    date = Column(String)
    open = Column(String)
    high = Column(String)
    low = Column(String)
    close = Column(String)
    adjclose = Column(String)
    volume = Column(String)


class StocksOptional(BaseModel):
    open: Optional[str]
    high: Optional[str]
    low: Optional[str]
    close: Optional[str]
    adjclose: Optional[str]
    volume: Optional[str]
