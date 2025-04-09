from fastapi import FastAPI
from olx_scraper import scrap_olx_data

app = FastAPI()

@app.get("/")
def root():
    return{"Hello world"}

@app.get("/scrap")
def scrap_olx():
    result = scrap_olx_data()
    return result