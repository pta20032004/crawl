# crawlers/tuoitre_parser.py

import re
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup

def parse_tuoitre_articles(html_content: str) -> list:
    """
    Trích xuất các bài viết mới từ HTML của báo Tuổi Trẻ bằng BeautifulSoup.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'lxml')
    results = []
    unique_links = set()
    base_url = 'https://tuoitre.vn'

    tz_vietnam = timezone(timedelta(hours=7))
    now_utc = datetime.now(timezone.utc)
    two_hours_ago = now_utc - timedelta(hours=2)

    article_links = soup.find_all('a', class_='box-category-link-title')

    for link_tag in article_links:
        try:
            relative_link = link_tag.get('href')
            title = link_tag.get('title', link_tag.get_text(strip=True))

            if not relative_link or not title:
                continue

            match = re.search(r'-(\d{17})\.htm', relative_link)
            if not match:
                continue

            timestamp_str = match.group(1)
            publish_time_str = timestamp_str[:14]
            publish_date = datetime.strptime(publish_time_str, '%Y%m%d%H%M%S')
            
            publish_date_aware = publish_date.replace(tzinfo=tz_vietnam)
            publish_date_utc = publish_date_aware.astimezone(timezone.utc)
            
            if publish_date_utc >= two_hours_ago:
                full_link = base_url + relative_link

                if full_link in unique_links:
                    continue
                
                unique_links.add(full_link)
                formatted_publish_time = publish_date_aware.strftime('%d/%m/%Y %H:%M:%S')

                results.append({
                    'link': full_link,
                    'title': title.strip(),
                    'publish_time': formatted_publish_time
                })

        except (ValueError, IndexError) as e:
            print(f"Lỗi khi xử lý link của Tuổi Trẻ '{relative_link}': {e}")
            continue

    results.sort(key=lambda x: datetime.strptime(x['publish_time'], '%d/%m/%Y %H:%M:%S'), reverse=True)
    return results

