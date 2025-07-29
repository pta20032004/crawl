import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def parse_tuoitre_articles(html_content: str) -> list:
    """
    Phân tích nội dung HTML từ trang Tuổi Trẻ Online để lấy các bài viết
    được đăng trong vòng 2 giờ gần nhất bằng cách trích xuất thời gian từ URL.
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

    # --- Tìm tất cả các link bài viết ---
    # Các link này thường nằm trong các thẻ h2 hoặc h3
    article_links = soup.select('h2 a[href], h3 a[href]')

    # Biểu thức chính quy (regex) để tìm chuỗi 14 chữ số ngay trước .htm
    # Ví dụ: "...-2025072910363144.htm" -> sẽ khớp với "2025072910363144"
    time_pattern = re.compile(r'(\d{14})\.htm$')

    for link_tag in article_links:
        try:
            link = link_tag['href'].strip()
            title = link_tag.get('title', '').strip() or link_tag.get_text(strip=True)
            
            # Bỏ qua các link không phải bài viết (ví dụ: link tới chuyên mục)
            if not link.endswith('.htm'):
                continue

            # Dùng regex để tìm chuỗi thời gian trong link
            match = time_pattern.search(link)
            if not match:
                continue
            
            datetime_str = match.group(1)
            publish_date = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
            
            # Gán múi giờ Việt Nam
            publish_date = vietnam_tz.localize(publish_date)

            # So sánh thời gian
            if two_hours_ago <= publish_date <= now:
                if not link.startswith('http'):
                    link = base_url + link
                
                formatted_publish_time = publish_date.strftime('%H:%M:%S %d/%m/%Y')
                
                results.append({
                    'title': title,
                    'link': link,
                    'publish_time': formatted_publish_time
                })

        except Exception as e:
            print(f"Bỏ qua một link của Tuổi Trẻ do lỗi: {e}")
            continue

    # Loại bỏ các bài viết trùng lặp
    unique_results = []
    seen_links = set()
    for item in results:
        if item['link'] not in seen_links:
            unique_results.append(item)
            seen_links.add(item['link'])
            
    return unique_results