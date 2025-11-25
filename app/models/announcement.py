from datetime import datetime, date
from sqlalchemy import String, Integer, BigInteger, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class AnnouncementDetail(Base):
    __tablename__ = "announcement_detail"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    html: Mapped[str] = mapped_column(Text, nullable=False)
    
    announcement: Mapped["Announcement"] = relationship("Announcement", back_populates="announcement_detail", uselist=False)

class Announcement(Base):
    __tablename__ = "announcement"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    announcementdetail_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("announcement_detail.id"), unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    board: Mapped[str] = mapped_column(String(255), nullable=False)
    written_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    view_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    target_url: Mapped[str] = mapped_column(String(255), nullable=False)
    scraping_key: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    major: Mapped[str | None] = mapped_column(String(255), nullable=True)

    announcement_detail: Mapped["AnnouncementDetail"] = relationship("AnnouncementDetail", back_populates="announcement")
