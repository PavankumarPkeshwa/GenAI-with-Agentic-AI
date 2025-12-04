from app.agent.manager_agent import ingest_url

def scrape_single(url: str) -> dict:
    return ingest_url(url)
