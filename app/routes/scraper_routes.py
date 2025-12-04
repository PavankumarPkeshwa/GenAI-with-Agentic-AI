from fastapi import APIRouter, Query
from app.scraper.scraper import scrape_single
from app.scraper.cron import run_cron_job

router = APIRouter(prefix="/scraper", tags=["Scraper"])

@router.get("/scrape")
def scrape_url(url: str = Query(...)):
    return scrape_single(url)

@router.get("/cron")
def cron_run():
    return run_cron_job()
