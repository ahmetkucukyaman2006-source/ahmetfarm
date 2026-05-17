FROM python:3.12-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Gerekli sistem paketlerini kur (varsa)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Proje dosyalarını kopyala
COPY . .

# Flask uygulamasının çalışacağı port
EXPOSE 5000

# Gunicorn ile uygulamayı başlat
# run:app -> run.py dosyasındaki app nesnesini işaret eder
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
