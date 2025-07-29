import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def parse_tuoitre_articles(html_content: str) -> list:
    """
    Phân tích nội dung HTML từ trang Tuổi Trẻ Online để lấy các bài viết
    được đăng trong vòng 2 giờ gần nhất.

    Args:
        html_content: Chuỗi chứa nội dung HTML của trang web.

    Returns:
        Một danh sách các dictionary, mỗi dictionary chứa thông tin 
        về một bài viết (title, link, publish_time).
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'lxml')
    results = []
    base_url = 'https://tuoitre.vn'
    
    # --- Thiết lập múi giờ và thời gian ---
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vietnam_tz)
    # --- Logic đã cập nhật: Tìm trong vòng 2 giờ ---
    two_hours_ago = now - timedelta(hours=2)

    # --- Logic đã cập nhật: Tìm tất cả các thẻ <a> để không bỏ sót ---
    article_links = soup.find_all('a', href=True)

    # --- Logic đã cập nhật: Regex linh hoạt hơn ---
    time_pattern = re.compile(r'-(\d{14})\d*\.htm')

    for link_tag in article_links:
        try:
            link = link_tag.get('href', '').strip()
            title = link_tag.get('title', '').strip() or link_tag.get_text(strip=True)
            
            if not link.endswith('.htm') or not title:
                continue

            match = time_pattern.search(link)
            if not match:
                continue
            
            datetime_str = match.group(1)
            publish_date = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
            
            publish_date = vietnam_tz.localize(publish_date)

            # So sánh thời gian trong vòng 2 giờ
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
            # Bỏ qua nếu có lỗi ở một link và tiếp tục với các link khác
            # print(f"Bỏ qua link '{link}' do lỗi: {e}")
            continue

    # Loại bỏ các bài viết trùng lặp link
    unique_results = []
    seen_links = set()
    for item in results:
        if item['link'] not in seen_links:
            unique_results.append(item)
            seen_links.add(item['link'])
            
    return unique_results

# --- Ví dụ cách sử dụng ---
if __name__ == '__main__':
    # Để chạy thử, bạn cần tạo file 'test_page.html' 
    # và dán nội dung HTML của trang Tuổi Trẻ vào đó.
    try:
        with open('test_page.html', 'r', encoding='utf-8') as f:
            sample_html = f.read()
            
        # Tiền xử lý nếu cần (ví dụ: file có ký tự lỗi)
        sample_html = sample_html.replace('\\"', '"')

        articles = parse_tuoitre_articles(sample_html)
        
        print(f"Tìm thấy {len(articles)} bài viết trong vòng 2 giờ qua:")
        print("----------------------------------------------------")
        for article in articles:
            print(f"Tiêu đề: {article['title']}")
            print(f"Link: {article['link']}")
            print(f"Thời gian: {article['publish_time']}\n")

    except FileNotFoundError:
        print("Vui lòng tạo file 'test_page.html' để chạy ví dụ.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
