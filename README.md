# 🔐 Dijital İmza Oluşturma ve Doğrulama Aracı

Bilgisayar güvenliği dersi kapsamında geliştirilen, **RSA-PSS + SHA-256** tabanlı dijital imza oluşturma, doğrulama ve basit PKI simülasyonu içeren Python/Flask web uygulamasıdır.

## 📋 Özellikler

- **Anahtar Çifti Oluşturma** — RSA-2048/4096 public/private key üretimi
- **X.509 Sertifika Üretimi** — Demo Root CA tarafından imzalı sertifika
- **Dijital İmzalama** — Metin ve dosya imzalama (SHA-256 hash → Prehashed → RSA-PSS)
- **İmza Doğrulama** — Public key veya sertifika ile doğrulama
- **PKI Simülasyonu** — Kalıcı Demo Root CA, sertifika zinciri doğrulama
- **Güvenlik** — Private key sunucuda saklanmaz, kullanıcıya indirilir

## 📸 Ekran Görüntüleri (Screenshots)

Aşağıdaki ekran görüntülerini `static/img/` klasörüne ekleyerek projenizin vitrinini zenginleştirebilirsiniz:

- **Anahtar Üretimi:** `![Anahtar Oluşturma](static/img/screenshot-keys.png)`
- **İmzalama Ekranı:** `![İmzalama](static/img/screenshot-sign.png)`
- **Sertifika ve Doğrulama:** `![Doğrulama](static/img/screenshot-verify.png)`

## 🛠️ Teknolojiler

| Teknoloji | Kullanım |
|---|---|
| Python 3.12+ | Ana dil |
| Flask 3.1 | Web framework |
| cryptography 44.x | RSA, X.509, SHA-256 |
| SQLAlchemy + SQLite | Veritabanı |
| Jinja2 | HTML şablonları |
| Docker | Containerization |

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.10+
- pip

### Yerel Kurulum

```bash
# 1. Repoyu klonla
git clone https://github.com/mcpaslan/dijital-kimlik-olusturma-araci.git
cd dijital-kimlik-olusturma-araci

# 2. Sanal ortam oluştur ve aktifleştir
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Uygulamayı başlat
python app.py
```

Uygulama **http://127.0.0.1:5001** adresinde açılacaktır.

> İlk başlatmada Demo Root CA otomatik olarak `storage/ca/` altında oluşturulur.

### Docker ile Çalıştırma

```bash
# Image oluştur
docker build -t dijital-imza .

# Container başlat
docker run -d \
  --name dijital-imza-app \
  -p 5001:5000 \
  -v ./storage:/app/storage \
  -v ./instance:/app/instance \
  dijital-imza
```

## 📁 Proje Yapısı

```
├── app.py                      # Flask uygulama giriş noktası
├── config.py                   # Konfigürasyon ayarları
├── requirements.txt            # Python bağımlılıkları
├── Dockerfile                  # Docker tanımı
├── modules/                    # İş mantığı modülleri
│   ├── ca_manager.py           #   Demo Root CA yönetimi
│   ├── key_manager.py          #   RSA anahtar çifti üretimi
│   ├── certificate_manager.py  #   X.509 sertifika işlemleri
│   ├── signer.py               #   Dijital imzalama (Prehashed)
│   └── verifier.py             #   İmza doğrulama
├── models/
│   └── database.py             # SQLite modelleri (User, Certificate)
├── routes/                     # Flask endpoint'leri
│   ├── keys.py                 #   Anahtar oluşturma
│   ├── certificates.py         #   Sertifika işlemleri
│   ├── signing.py              #   İmzalama
│   └── verification.py         #   Doğrulama
├── templates/                  # HTML şablonları (Jinja2)
├── static/                     # CSS, JavaScript
└── storage/                    # Kalıcı dosyalar (CA, imzalar)
```

## 🔄 Kullanım Akışı

```
1. Anahtar Oluştur  →  RSA-2048/4096 key pair üret, private key'i indir
2. Sertifika Üret   →  Demo CA tarafından imzalı X.509 sertifika oluştur
3. İmzala           →  Metin veya dosyayı private key ile imzala
4. Doğrula          →  İmzayı public key veya sertifika ile doğrula
```

## 🔑 Kullanılan Algoritmalar

| Algoritma | Açıklama |
|---|---|
| **RSA-PSS** | Probabilistic Signature Scheme — dijital imza |
| **SHA-256** | Kriptografik hash fonksiyonu |
| **Prehashed** | Çift hash'lemeyi önleyen imzalama yöntemi |
| **X.509** | Dijital sertifika standardı |

## 👥 Ekip

5 kişilik ekip tarafından geliştirilmektedir.

## 📄 Lisans

Bu proje eğitim amaçlıdır.
