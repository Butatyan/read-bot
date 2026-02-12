FROM python:3.13-slim

# ffmpeg を入れる
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

# 依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソース
COPY . .

CMD ["python", "read_bot.py"]
