from datetime import date
from pydantic import BaseModel

class ArticleOrigin(BaseModel):
    code: str  # 게시판 식별자
    name: str
    target_url: str


class ArticleContent(BaseModel):
    id: str    # 스크래핑 게시물 식별자
    link: str  # link 필드에 제목이 들어감
    date: str  # date 필드에 작성자가 들어감
    body: str  # html
    original_url: str
    written_at: date


class Article(BaseModel):
    origin: ArticleOrigin
    contents: ArticleContent


class WebhookAnnouncementRequest(BaseModel):
    article: Article
