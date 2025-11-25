from typing import List
from datetime import datetime, date
from bs4 import BeautifulSoup, Comment
from app.scrapers.base import BaseScraper, ScrapedItem, ScrapedDetail
import re

class ScholarScraper(BaseScraper):
    async def parse_list(self, html: str, base_url: str) -> List[ScrapedItem]:
        soup = BeautifulSoup(html, "html.parser")
        items = []

        rows = soup.select("div#subConWarp form table tbody tr")
        print(f"Found {len(rows)} rows in HTML")

        for row in rows:
            try:
                display_id_elem = row.select_one("td:nth-child(1)")
                display_id = display_id_elem.get_text(strip=True)
                if "공지" in display_id:
                    continue

                anchor = row.select_one("td a")
                href = anchor.get("href")

                match = re.search(r"fnView\('([^']*)',\s*'([^']*)'\)", href)
                date = match.group(1)
                seq = match.group(2)

                view_url = f"https://scholarship.uos.ac.kr/scholarship/notice/notice/view.do?brdDate={date}&brdSeq={seq}&brdBbsseq=1&identified=anonymous"

                parsed_date = datetime.strptime(date, "%Y%m%d").date()
                view_count = int(row.select_one("td:nth-child(5)").get_text(strip=True))

                items.append(ScrapedItem(
                    id=display_id,
                    url=view_url,
                    date=parsed_date,
                    view_count=view_count,
                ))
            except Exception as e:
                print(f"Error parsing row: {e}")
                raise e

        return items

    async def parse_detail(self, html: str) -> ScrapedDetail:
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("#subConWarp > table > thead > tr > td.left_L.fontBold").text.strip()
        author = soup.select_one("#subConWarp > table > tbody > tr:nth-child(1) > td:nth-child(2)").text.strip()

        content = soup.select_one("#td_content")
        for comment in content.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        for tag in content.find_all(True):
            if tag.has_attr('style'):
                del tag['style']
            if tag.has_attr('class'):
                del tag['class']
            if tag.has_attr('lang'):
                del tag['lang']

        cleaned_content = content.decode_contents()
        cleaned_content = cleaned_content.replace('\uFEFF', '').replace('\u200B', '').replace('\u00A0', ' ')
        cleaned_content = cleaned_content.strip()

        return ScrapedDetail(
            title=title,
            html=cleaned_content,
            author=author,
        )
