import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def parse_dantri_articles(html_content: str) -> list:
    """
    Phân tích nội dung HTML từ trang Dân trí để lấy các bài viết được đăng
    trong vòng 2 giờ gần nhất.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'lxml')
    results = []
    base_url = 'https://dantri.com.vn'
    
    # --- Thiết lập múi giờ và thời gian ---
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vietnam_tz)
    two_hours_ago = now - timedelta(hours=2)

    # --- Tìm tất cả các khối bài viết ---
    article_blocks = soup.find_all('article', class_='article-item')

    # Biểu thức chính quy (regex) để tìm chuỗi 14 chữ số (YYYYMMDDHHMMSS)
    # Ví dụ: "...-20250729094728890.htm" -> sẽ khớp với "20250729094728"
    time_pattern = re.compile(r'(\d{14})')

    for block in article_blocks:
        try:
            link_tag = block.find('a', href=True)
            if not link_tag:
                continue

            link = link_tag['href'].strip()
            
            # Lấy tiêu đề từ thẻ con hoặc thuộc tính title
            title_tag_h3 = block.find('h3', class_='article-title')
            title = title_tag_h3.get_text(strip=True) if title_tag_h3 else "Không có tiêu đề"

            # Dùng regex để tìm chuỗi thời gian trong link
            match = time_pattern.search(link)
            if not match:
                continue
            
            datetime_str = match.group(1)
            publish_date = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
            
            # Gán múi giờ Việt Nam cho thời gian vừa trích xuất
            publish_date = vietnam_tz.localize(publish_date)

            # So sánh với mốc 2 giờ trước
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
            # Bỏ qua nếu có lỗi ở một khối và tiếp tục
            print(f"Bỏ qua một khối bài viết do lỗi: {e}")
            continue
    
    # Loại bỏ các bài viết trùng lặp nếu có
    unique_results = []
    seen_links = set()
    for item in results:
        if item['link'] not in seen_links:
            unique_results.append(item)
            seen_links.add(item['link'])
            
    return unique_results