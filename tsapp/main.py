from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .models import Stocks, Base
from .database import SessionLocal, engine

import datetime
import time
import urllib.request
import csv
import json

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/get")
def automatedata(id:int,db: Session = Depends(get_db)):
    date_obj = datetime.datetime.now()
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    last_year = int(datetime.datetime(year - 1, month, day, 0, 0, 0).timestamp())
    curr_year = int(time.time())
    with open("company.json","r") as file:
        jsonObj= json.load(file)

    for key in jsonObj:
        if int(key) == id:
            company_name = jsonObj[key]
            data_url = f"https://query1.finance.yahoo.com/v7/finance/download/{company_name}?period1={last_year}&period2={curr_year}&interval=1d&events=history&includeAdjustedClose=true"
            urllib.request.urlretrieve(data_url, f"{company_name}.csv")
            db.query(Stocks).filter(Stocks.company_id == int(key)).delete()
            with open(f"{company_name}.csv", "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data = Stocks(
                        company_id=key,
                        date=row["Date"],
                        open=row["Open"],
                        high=row["High"],
                        low=row["Low"],
                        close=row["Close"],
                        adjclose=row["Adj Close"],
                        volume=row["Volume"],
                    )
                    db.add(data)
                    db.commit()
            return db.query(Stocks).all()
    return "No such company with id"
