from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .models import Stocks, Base,StocksOptional
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


# Load the company config
with open("company.json", "r") as file:
    jsonObj = json.load(file)

################## Automation Section #################

# Load company datas on startup
@app.on_event("startup")
async def automatedata():
    with SessionLocal() as db:
        print("Fetching company details..")
        date_obj = datetime.datetime.now()
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        last_year = int(datetime.datetime(year - 1, month, day, 0, 0, 0).timestamp())
        curr_year = int(time.time())

        for key in jsonObj:
            company_name = jsonObj[key]
            data_url = f"https://query1.finance.yahoo.com/v7/finance/download/{company_name}?period1={last_year}&period2={curr_year}&interval=1d&events=history&includeAdjustedClose=true"
            urllib.request.urlretrieve(data_url, f"{company_name}.csv")
            db.query(Stocks).filter(Stocks.company_id == int(key)).delete()
            with open(f"{company_name}.csv", "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data = Stocks(
                        company_id=key,
                        company_name=company_name,
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
            print(f"{company_name} data added")


############ API Section ####################

# Get company data by id
@app.get("/api/get/by_id")
def getCompanyById(id: int, db: Session = Depends(get_db)):
    if str(id) in jsonObj:
        return db.query(Stocks).filter(Stocks.company_id == id).all()
    return "No such company id exist"


# Get all company data by date
@app.get("/api/get/all")
def getAllCompaniesByDate(date: str, db: Session = Depends(get_db)):
    res = db.query(Stocks).filter(Stocks.date == date).all()
    if len(res) > 0:
        return res
    return "No record with the specified date exist"

# Get specific company data by date
@app.get("/api/get/custom/by_id")
def getCustomDataById(id: int, date: str, db: Session = Depends(get_db)):
    if str(id) in jsonObj:
        res = (
            db.query(Stocks).filter(Stocks.date == date, Stocks.company_id == id).all()
        )
        if len(res) > 0:
            return res
        return "No record with the specified date exist"
    return "No such company id exist"

# Update data by company id and date
@app.patch("/api/update")
def updateCompanyData(id: int,date: str,request:StocksOptional,db:Session=Depends(get_db)):
    curr_data = db.query(Stocks).filter(Stocks.date==date,Stocks.company_id==id)
    if not curr_data.first():
        return "company id or date is wrong"

    new_data = dict((k, v) for k, v in dict(request).items() if v)
    curr_data.update(new_data)
    db.commit()
    return curr_data.first()
