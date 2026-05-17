FROM python:3.12-slim

WORKDIR /app

# Bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Gerekli dizinleri oluştur
RUN mkdir -p storage/ca storage/uploads storage/signatures instance

ENV PORT=5000
EXPOSE 5000

# Gunicorn ile çalıştır
CMD ["python", "app.py"]
