from fastapi import FastAPI, Query
from scraper import AzoraScraper

app = FastAPI(title="Azora Moon API")
scraper = AzoraScraper()

@app.get("/fetch")
async def fetch_manga(url: str = Query(..., description="رابط المانجا أو الفصل")):
    data = await scraper.get_page_content(url)
    return data
