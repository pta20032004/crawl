# crawlers/dantri_parser.py

import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def parse_dantri_articles(html_content: str) -> list:
    """
    Phân tích nội dung HTML từ trang Dân trí để lấy các bài viết mới.

    Args:
        html_content (str): Chuỗi chứa nội dung HTML của trang web.

    Returns:
        list: Danh sách các bài viết được đăng trong vòng 2 giờ qua.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    results = []
    base_url = 'https://dantri.com.vn'
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vietnam_tz)
    two_hours_ago = now - timedelta(hours=2)

    article_blocks = soup.find_all('article', class_='article-item')
    if not article_blocks:
        return []

    for block in article_blocks:
        try:
            title_tag = block.find('h3', class_='article-title')
            link_tag = title_tag.find('a') if title_tag else None
            
            data_track_content = block.get('data-track-content')
            if not data_track_content:
                continue

            parts = data_track_content.split('-')
            timestamp_str_with_ext = parts[-1]
            timestamp_str = timestamp_str_with_ext.split('.')[0]

            if len(timestamp_str) < 14:
                continue

            if link_tag and 'href' in link_tag.attrs:
                link = link_tag['href'].strip()
                title = link_tag.get_text(strip=True)

                if not link.startswith('http'):
                    link = base_url + link

                publish_date_naive = datetime.strptime(timestamp_str[:14], "%Y%m%d%H%M%S")
                publish_date = vietnam_tz.localize(publish_date_naive)
                
                if two_hours_ago <= publish_date <= now:
                    formatted_publish_time = publish_date.strftime('%d/%m/%Y, %H:%M:%S')
                    results.append({
                        'link': link,
                        'title': title,
                        'publish_time': formatted_publish_time
                    })

        except (AttributeError, ValueError, IndexError) as e:
            print(f"Lỗi khi xử lý một khối bài viết của Dân Trí: {e}")
            continue
            
    unique_results = []
    seen_links = set()
    for item in results:
        if item['link'] not in seen_links:
            unique_results.append(item)
            seen_links.add(item['link'])

    return unique_results
