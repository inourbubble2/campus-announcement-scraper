from datetime import datetime
import enum
from sqlalchemy import String, Integer, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class ScraperType(str, enum.Enum):
    COMMON = "COMMON"
    SCHOLAR = "SCHOLAR"
    # Add other types here as needed

class TargetOrigin(Base):
    __tablename__ = "target_origins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    target_url: Mapped[str] = mapped_column(String, nullable=False)
    scraper_type: Mapped[ScraperType] = mapped_column(Enum(ScraperType), nullable=False)
    scrap_interval: Mapped[int] = mapped_column(Integer, nullable=False) # Minutes
    board: Mapped[str] = mapped_column(String, nullable=False)
    major: Mapped[str | None] = mapped_column(String, nullable=True)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
