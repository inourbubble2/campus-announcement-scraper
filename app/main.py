import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import get_db, engine, Base, AsyncSessionLocal
from app.models.origin import TargetOrigin
from app.services.scraper_service import ScraperService
from app.schemas.scrape import DateRangeRequest

# Scheduler Setup
scheduler = AsyncIOScheduler()
scraper_service = ScraperService()

async def run_scraper_job(origin_id: int):
    async with AsyncSessionLocal() as session:
        stmt = select(TargetOrigin).where(TargetOrigin.id == origin_id)
        result = await session.execute(stmt)
        origin = result.scalar_one_or_none()
        
        if origin:
            print(f"Starting job for {origin.name}")
            await scraper_service.scrape(origin, session)
            print(f"Finished job for {origin.name}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Load jobs
    async with AsyncSession(engine) as session:
        stmt = select(TargetOrigin)
        result = await session.execute(stmt)
        origins = result.scalars().all()
        
        for origin in origins:
            scheduler.add_job(
                run_scraper_job,
                IntervalTrigger(minutes=origin.scrap_interval),
                id=str(origin.id),
                args=[origin.id],
                replace_existing=True
            )
            print(f"Scheduled job for {origin.name} every {origin.scrap_interval} minutes")

    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(title="UOS Scraper", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/v1/origins/{origin_id}/scrape")
async def trigger_scrape(origin_id: int, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    stmt = select(TargetOrigin).where(TargetOrigin.id == origin_id)
    result = await db.execute(stmt)
    origin = result.scalar_one_or_none()
    
    if not origin:
        raise HTTPException(status_code=404, detail="Origin not found")
    
    background_tasks.add_task(run_scraper_job, origin.id)
    return {"message": "Scraping triggered in background"}

@app.post("/api/v1/origins/{origin_id}/scrape-range")
async def scrape_range(
    origin_id: int, 
    request: DateRangeRequest, 
    db: AsyncSession = Depends(get_db)
):
    stmt = select(TargetOrigin).where(TargetOrigin.id == origin_id)
    result = await db.execute(stmt)
    origin = result.scalar_one_or_none()
    
    if not origin:
        raise HTTPException(status_code=404, detail="Origin not found")
    
    count = await scraper_service.scrape_range(origin, request.start_date, request.end_date, db)
    return {"message": f"Scraped {count} items between {request.start_date} and {request.end_date}"}
