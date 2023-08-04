# 使用官方的 Python 基礎映像
FROM python:3.11.4

#RUN mkdir /rules

# 複製當前目錄下的所有檔案到容器的 /app 目錄
COPY ./src /app
#COPY ./rules /rules
COPY requirements.txt /app

# 設定工作目錄
WORKDIR /app

# 安裝需要的 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 在容器啟動時執行 b_yaraScanner.py
CMD ["python", "main.py"]