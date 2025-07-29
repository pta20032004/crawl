# main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import traceback

# Import các hàm parser từ thư mục crawlers
from crawlers.dantri_parser import parse_dantri_articles
from crawlers.tuoitre_parser import parse_tuoitre_articles

# --- Pydantic Model để định nghĩa cấu trúc JSON đầu vào ---
# Model này yêu cầu một JSON object có key là "data" và giá trị là một chuỗi (string)
class N8nPayload(BaseModel):
    data: str = Field(..., description="Nội dung HTML được gửi từ n8n hoặc client khác dưới dạng chuỗi.")

# --- Khởi tạo ứng dụng FastAPI ---
app = FastAPI(
    title="API Crawler Báo Chí",
    description="API nhận file HTML hoặc dữ liệu JSON để trích xuất các bài báo mới từ Dân Trí và Tuổi Trẻ.",
    version="1.1.0"
)

# --- Endpoint Chào Mừng ---
@app.get("/", summary="Endpoint chào mừng")
def read_root():
    """Endpoint gốc để kiểm tra API có hoạt động không."""
    return {"message": "Chào mừng đến với API Crawler."}

# --- CÁC ENDPOINT MỚI ĐỂ NHẬN JSON (DÀNH CHO N8N) ---

@app.post("/crawl-json/dantri", summary="Crawl Dân Trí từ dữ liệu JSON")
async def crawl_dantri_from_json(payload: N8nPayload):
    """
    Nhận một payload JSON có chứa nội dung HTML (ví dụ: từ n8n),
    phân tích và trích xuất các bài viết mới nhất từ **Dân Trí**.
    """
    try:
        # Lấy nội dung HTML từ payload.data
        html_content = payload.data
        articles = parse_dantri_articles(html_content)
        
        if not articles:
            return JSONResponse(status_code=200, content={"message": "Không tìm thấy bài viết mới nào trong 2 giờ qua.", "data": []})
            
        return {"message": f"Tìm thấy {len(articles)} bài viết mới.", "data": articles}
        
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi server: {e}")

@app.post("/crawl-json/tuoitre", summary="Crawl Tuổi Trẻ từ dữ liệu JSON")
async def crawl_tuoitre_from_json(payload: N8nPayload):
    """
    Nhận một payload JSON có chứa nội dung HTML (ví dụ: từ n8n),
    phân tích và trích xuất các bài viết mới nhất từ **Tuổi Trẻ**.
    """
    try:
        # Lấy nội dung HTML từ payload.data
        html_content = payload.data
        articles = parse_tuoitre_articles(html_content)
        
        if not articles:
            return JSONResponse(status_code=200, content={"message": "Không tìm thấy bài viết mới nào trong 2 giờ qua.", "data": []})
        
        return {"message": f"Tìm thấy {len(articles)} bài viết mới.", "data": articles}
        
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi server: {e}")

# --- CÁC ENDPOINT CŨ ĐỂ UPLOAD FILE (VẪN GIỮ LẠI) ---

@app.post("/crawl/dantri", summary="Crawl Dân Trí từ file HTML", deprecated=True)
async def crawl_dantri_from_file(file: UploadFile = File(..., description="File HTML của trang Dân Trí cần phân tích.")):
    """
    (Endpoint cũ) Nhận một tệp HTML, phân tích và trích xuất các bài viết mới nhất
    từ **Dân Trí** được đăng trong vòng 2 giờ qua.
    """
    if file.content_type != "text/html":
        raise HTTPException(status_code=400, detail="Định dạng file không hợp lệ. Vui lòng tải lên file HTML.")
    
    try:
        html_content = await file.read()
        articles = parse_dantri_articles(html_content.decode('utf-8'))
        
        if not articles:
            return JSONResponse(status_code=200, content={"message": "Không tìm thấy bài viết mới nào trong 2 giờ qua.", "data": []})
            
        return {"message": f"Tìm thấy {len(articles)} bài viết mới.", "data": articles}
        
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi server: {e}")

@app.post("/crawl/tuoitre", summary="Crawl Tuổi Trẻ từ file HTML", deprecated=True)
async def crawl_tuoitre_from_file(file: UploadFile = File(..., description="File HTML của trang Tuổi Trẻ cần phân tích.")):
    """
    (Endpoint cũ) Nhận một tệp HTML, phân tích và trích xuất các bài viết mới nhất
    từ **Tuổi Trẻ** được đăng trong vòng 2 giờ qua.
    """
    if file.content_type != "text/html":
        raise HTTPException(status_code=400, detail="Định dạng file không hợp lệ. Vui lòng tải lên file HTML.")

    try:
        html_content = await file.read()
        articles = parse_tuoitre_articles(html_content.decode('utf-8'))
        
        if not articles:
            return JSONResponse(status_code=200, content={"message": "Không tìm thấy bài viết mới nào trong 2 giờ qua.", "data": []})
        
        return {"message": f"Tìm thấy {len(articles)} bài viết mới.", "data": articles}
        
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi server: {e}")
