from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.origin import TargetOrigin, ScraperType
from app.models.announcement import Announcement, AnnouncementDetail
from app.scrapers.base import BaseScraper, ScrapedItem
from app.scrapers.common import CommonScraper
from app.scrapers.scholar import ScholarScraper
from app.core.clients import RateLimitedClient

class ScraperService:
    def __init__(self):
        self.client = RateLimitedClient(
            interval=1.0,
            timeout=10.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        self.scrapers = {
            ScraperType.COMMON: CommonScraper(),
            ScraperType.SCHOLAR: ScholarScraper(),
            # Add other scrapers here
        }

    async def _fetch_items_generator(self, origin: TargetOrigin, start_page: int = 1):
        """
        Yields items from the target URL, handling pagination.
        """
        scraper = self.scrapers.get(origin.scraper_type, self.scrapers[ScraperType.COMMON])
        page = start_page

        while True:
            list_url = f"{origin.target_url}&pageIndex={page}"
            print(f"Fetching URL: {list_url}")

            response = await self.client.get(list_url)
            response.raise_for_status()

            items = await scraper.parse_list(response.text, origin.target_url)

            if not items:
                print("No items found on page, stopping.")
                break

            for item in items:
                yield item, page

            page += 1

    async def _process_and_save_item(self, origin: TargetOrigin, item: ScrapedItem, scraper: BaseScraper, db: AsyncSession):
        """
        Processes a single item: checks duplicates, fetches detail, and saves to DB.
        Returns True if saved, False if skipped/failed.
        """
        # Check duplicate in DB
        scraping_key = f"{origin.code}-{item.id}"
        stmt = select(Announcement).where(Announcement.scraping_key == scraping_key)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            return

        # Fetch Detail
        try:
            response = await self.client.get(item.url)
            scraped_detail = await scraper.parse_detail(response.text)
        except Exception as e:
            print(f"Failed to fetch detail for {item.url}: {e}")
            raise e

        # Save
        announcement_detail = AnnouncementDetail(url=item.url, html=scraped_detail.html)
        announcement = Announcement(
            title=scraped_detail.title,
            author=scraped_detail.author,
            board=origin.board,
            target_url=origin.target_url,
            major=origin.major,
            scraping_key=scraping_key,
            written_at=item.date,
            view_count=item.view_count,
            announcement_detail=announcement_detail
        )

        db.add(announcement)

    async def scrape(self, origin: TargetOrigin, db: AsyncSession):
        scraper = self.scrapers.get(origin.scraper_type, self.scrapers[ScraperType.COMMON])
        total_scraped = 0

        # Scrape only the first page (or until items run out on first page)
        async for item, page in self._fetch_items_generator(origin):
            if page > 1:
                break

            if item.is_notice:
                print(f"Skipping notice: {item.url}")
                continue

            await self._process_and_save_item(origin, item, scraper, db)
            total_scraped += 1

        await db.commit()
        return total_scraped

    async def scrape_range(self, origin: TargetOrigin, start_date: date, end_date: date, db: AsyncSession):
        scraper = self.scrapers.get(origin.scraper_type, self.scrapers[ScraperType.COMMON])
        total_scraped = 0

        print(f"Scraping range: {start_date} ~ {end_date} for {origin.name}")

        async for item, page in self._fetch_items_generator(origin):
            print(f"Checking item: {origin.code}-{item.id}")

            if item.date < start_date:
                print(f"Item date {item.date} is older than start date {start_date}, stopping.")
                break
            elif item.date > end_date:
                print(f"Item date {item.date} is newer than end date {end_date}, skipping.")
                continue

            await self._process_and_save_item(origin, item, scraper, db)
            total_scraped += 1

        await db.commit()
        return total_scraped
