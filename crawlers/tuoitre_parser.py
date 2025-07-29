import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def parse_tuoitre_articles(html_content: str) -> list:
    """
    Phân tích nội dung HTML từ trang Tuổi Trẻ Online để lấy các bài viết
    được đăng trong vòng 2 giờ gần nhất.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'lxml')
    results = []
    base_url = 'https://tuoitre.vn'
    
    # --- Thiết lập múi giờ và thời gian ---
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vietnam_tz)
    two_hours_ago = now - timedelta(hours=2)

    # --- Tìm tất cả các thẻ h2 và h3 có thuộc tính data-id ---
    # Đây là các thẻ chứa tiêu đề và link của bài viết
    article_headers = soup.find_all(['h2', 'h3'], attrs={'data-id': True})
    
    # Biểu thức chính quy (regex) để lấy 14 chữ số đầu tiên
    time_pattern = re.compile(r'^(\d{14})')

    for header in article_headers:
        try:
            link_tag = header.find('a', href=True)
            if not link_tag:
                continue

            link = link_tag['href'].strip()
            title = link_tag.get('title', '').strip() or link_tag.get_text(strip=True)
            
            # Lấy chuỗi ID từ thuộc tính data-id
            article_id = header.get('data-id', '')
            
            # Dùng regex để trích xuất chuỗi thời gian
            match = time_pattern.search(article_id)
            if not match:
                continue
            
            datetime_str = match.group(1)
            publish_date = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
            
            # Gán múi giờ Việt Nam cho thời gian vừa trích xuất
            publish_date = vietnam_tz.localize(publish_date)

            # So sánh thời gian
            if two_hours_ago <= publish_date <= now:
                # Hoàn thiện URL nếu nó là đường dẫn tương đối
                if not link.startswith('http'):
                    link = base_url + link
                
                formatted_publish_time = publish_date.strftime('%H:%M:%S %d/%m/%Y')
                
                results.append({
                    'title': title,
                    'link': link,
                    'publish_time': formatted_publish_time
                })

        except Exception as e:
            print(f"Bỏ qua một khối bài viết của Tuổi Trẻ do lỗi: {e}")
            continue

    # Loại bỏ các bài viết trùng lặp vì có thể xuất hiện ở nhiều mục
    unique_results = []
    seen_links = set()
    for item in results:
        if item['link'] not in seen_links:
            unique_results.append(item)
            seen_links.add(item['link'])
            
    return unique_results