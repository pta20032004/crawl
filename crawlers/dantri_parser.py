# crawlers/dantri_parser.py (phiên bản đã sửa)

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def parse_dantri_articles(html_content: str) -> list:
    """
    Phân tích nội dung HTML từ trang Dân trí để lấy các bài viết mới.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    results = []
    base_url = 'https://dantri.com.vn'

    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vietnam_tz)
    two_hours_ago = now - timedelta(hours=2)

    article_blocks = soup.find_all('article', class_='article-item')

    for block in article_blocks:
        try:
            title_tag = block.find('h3', class_='article-title')
            link_tag = title_tag.find('a') if title_tag else None
            time_tag = block.find('time') # Tìm thẻ time

            if not link_tag or 'href' not in link_tag.attrs or not time_tag or 'datetime' not in time_tag.attrs:
                continue

            link = link_tag['href'].strip()
            title = link_tag.get_text(strip=True)

            # Lấy chuỗi thời gian từ thuộc tính datetime của thẻ <time>
            datetime_str = time_tag['datetime']
            # Chuyển chuỗi thời gian thành đối tượng datetime
            # Định dạng có thể là "2025-07-29T09:47:28+07:00", nên cần xử lý phù hợp
            publish_date = datetime.fromisoformat(datetime_str)

            # Chuyển về múi giờ Việt Nam nếu chưa có
            if publish_date.tzinfo is None:
                publish_date = vietnam_tz.localize(publish_date)

            if two_hours_ago <= publish_date <= now:
                if not link.startswith('http'):
                    link = base_url + link

                formatted_publish_time = publish_date.strftime('%d/%m/%Y, %H:%M:%S')
                results.append({
                    'link': link,
                    'title': title,
                    'publish_time': formatted_publish_time
                })

        except (AttributeError, ValueError, IndexError) as e:
            print(f"Lỗi khi xử lý một khối bài viết của Dân Trí: {e}")
            continue

    # Loại bỏ các bài viết trùng lặp
    unique_results = []
    seen_links = set()
    for item in results:
        if item['link'] not in seen_links:
            unique_results.append(item)
            seen_links.add(item['link'])

    return unique_results