# Sử dụng image Python chính thức
FROM python:3.9-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt ./

# Cài đặt các thư viện cần thiết từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của ứng dụng vào container
COPY . .

# Thiết lập cổng mặc định (thường là 5000 cho Flask)
EXPOSE 5000

# Lệnh khởi chạy ứng dụng Flask (có thể cập nhật sau)
CMD ["python", "app.py"]
