from abc import ABC, abstractmethod
from datetime import date
from typing import List
from pydantic import BaseModel

class ScrapedItem(BaseModel):
    id: str
    url: str
    date: date
    view_count: int = 0

class ScrapedDetail(BaseModel):
    title: str
    html: str
    author: str

class BaseScraper(ABC):
    @abstractmethod
    async def parse_list(self, html: str, base_url: str) -> List[ScrapedItem]:
        """Parse the list page HTML and return a list of items."""
        pass

    @abstractmethod
    async def parse_detail(self, html: str) -> ScrapedDetail:
        """Parse the detail page HTML and return the content HTML."""
        pass
