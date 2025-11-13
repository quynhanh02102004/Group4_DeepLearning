# Backend API Gợi Ý Thời Trang Thông Minh

Đây là mã nguồn cho phần backend của ứng dụng gợi ý thời trang, được xây dựng bằng FastAPI và kết nối với MongoDB Atlas. Ứng dụng cung cấp các API để tìm kiếm sản phẩm tương tự bằng hình ảnh và gợi ý các trang phục phối đồ.

## Yêu Cầu Hệ Thống

Trước khi bắt đầu, hãy đảm bảo bạn đã cài đặt các công cụ sau trên máy tính:

-   **Git:** [Tải tại đây](https://git-scm.com/downloads)
-   **Python:** Phiên bản 3.8 trở lên. [Tải tại đây](https://www.python.org/downloads/)

---

## Hướng Dẫn Cài Đặt và Chạy

Làm theo các bước dưới đây để cài đặt và chạy dự án trên máy của bạn.

### 1. Tải Mã Nguồn Về (Clone Repository)
Nếu muốn đọc code thì FastAPI nằm trong folder backend (link GitHub)

Mở Terminal (hoặc Command Prompt/PowerShell) và chạy lệnh sau để tải mã nguồn về máy:

```bash
git clone https://github.com/quynhanh02102004/Group4_DeepLearning.git
```
*(Lưu ý: Thay thế URL trên bằng URL đến repository của bạn nếu khác.)*

Sau đó, di chuyển vào thư mục của dự án:

```bash
cd yame-api-deploy
```

### 2. Thiết Lập Môi Trường Ảo

Sử dụng môi trường ảo là một bước rất quan trọng để quản lý các thư viện của dự án một cách độc lập.

```bash
# Tạo một môi trường ảo có tên là "venv"
python -m venv venv

# Kích hoạt môi trường ảo vừa tạo
# Trên Windows:
venv\Scripts\activate
# Trên macOS hoặc Linux:
source venv/bin/activate
```
Sau khi kích hoạt, bạn sẽ thấy `(venv)` xuất hiện ở đầu dòng lệnh trong terminal.

### 3. Cài Đặt Các Thư Viện Cần Thiết

Tất cả các thư viện mà dự án yêu cầu đã được liệt kê trong file `requirements.txt`. Chạy lệnh sau để cài đặt chúng:

```bash
pip install -r requirements.txt
```
*maybe có thể phải cài thêm tại t chưa update lại thêm thư viện trong file nè*
### 4. Cấu Hình Biến Môi Trường

Ứng dụng cần thông tin để kết nối đến cơ sở dữ liệu MongoDB Atlas.

1.  Trong thư mục dự án, tìm file có tên `.env.example`.
2.  Tạo một bản sao của file này và đổi tên thành `.env`.
3.  Mở file `.env` và điền các thông tin của bạn vào:

    ```ini
    # Dán chuỗi kết nối MongoDB Atlas của bạn vào đây
    MONGO_URI="mongodb+srv://giang_db:040904@cluster0.tmediap.mongodb.net/?appName=Cluster0"

    # Tên database bạn đang sử dụng
    DB_NAME="Polyvore_outfits"
    ```
4.  Lưu file lại.

### 5. Chạy Server

Mọi thứ đã sẵn sàng! Hãy khởi động server backend. Chạy lệnh

```bash
python uvicorn_runner.py
```

Server sẽ khởi động. Lần đầu tiên chạy, ứng dụng sẽ **tự động tải về file model AI**. Quá trình này có thể mất vài phút. Khi hoàn tất, bạn sẽ thấy thông báo:
`Uvicorn running on http://0.0.0.0:8000`

### 6. Truy Cập và Kiểm Tra API

Mở trình duyệt web của bạn và truy cập vào địa chỉ sau để xem tài liệu API tương tác:

**`http://127.0.0.1:8000/docs`**

Tại đây, bạn có thể xem danh sách tất cả các API và bấm Try it out để test thử và trải nghiệm các API. 