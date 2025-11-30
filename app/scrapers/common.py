from typing import List
from datetime import datetime
from bs4 import BeautifulSoup, Comment
from app.scrapers.base import BaseScraper, ScrapedItem, ScrapedDetail
import re

class CommonScraper(BaseScraper):
    async def parse_list(self, html: str, base_url: str) -> List[ScrapedItem]:
        soup = BeautifulSoup(html, "html.parser")
        items = []

        # Selector based on UOS common list pattern
        rows = soup.select(".content-area #contents ul.brd-lstp1 li")
        print(f"Found {len(rows)} rows in HTML")

        for row in rows:
            try:
                num_text_elem = row.select_one("p.num")
                display_id = num_text_elem.get_text(strip=True)
                if "공지" in display_id:
                    continue

                # Extract ID from href (e.g., javascript:fnView('12345');
                # <div class="ti">
                # 	<a href="javascript:fnView('11', '29974');">
                # 		입학홍보대사 스카우터(Scouter) 18기 모집 공고 ♥
                # 	</a>
                # </div>
                ti_elem = row.select_one(".ti")
                href = ti_elem.find("a").get("href")
                seq = re.search(r"fnView\('([^']*)',\s*'([^']*)'\)", href).group(2)
                view_url = base_url.replace("list.do", "view.do") + f"&seq={seq}"

                # Date and Views are in .da spans
                # Structure: <span>Author</span> <span>Date</span> <span>ViewCount</span>
                da_elem = row.select_one(".da")
                spans = da_elem.find_all("span")
                date_str = spans[1].text.strip()
                parsed_date = datetime.strptime(date_str.replace(".", "-"), "%Y-%m-%d").date()
                view_count = int(spans[2].text.strip())

                items.append(ScrapedItem(
                    id=seq,
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

        title = soup.select_one("#contents > div > div.view-bx > div.vw-tibx > h4").text.strip()
        author = soup.select_one("#contents > div > div.view-bx > div.vw-tibx > div > div > span:nth-child(2)").text.strip()

        # Parse hashtags
        hashtag_elements = soup.select(".hashTag-bx a")
        tags = [tag.text.strip() for tag in hashtag_elements] if hashtag_elements else None

        content = soup.select_one(".vw-con")
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
            tags=tags,
        )
