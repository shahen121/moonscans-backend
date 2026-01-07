from fastapi import FastAPI
from scraper import AzoraScraper

app = FastAPI()
scraper = AzoraScraper()

@app.get("/")
async def root():
    return {"message": "Azora Moon API is Running!"}

@app.get("/manga-info")
async def get_manga(url: str):
    data = await scraper.get_page_content(url)
    return data
