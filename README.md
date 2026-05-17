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

## 🆕 Son Güncellemeler (feature/kritik-eksikler)

Bu branch'te aşağıdaki kritik eksikler tamamlandı:

- ✅ **16 MB dosya boyutu sınırı** — Büyük dosya yüklenince sunucu çökmez, şık hata sayfası gösterir
- ✅ **Türkçe hata mesajları** — Boş veya hatalı `.pem` dosyası yüklenince anlaşılır uyarı çıkar
- ✅ **E2E Testler (Playwright)** — Anahtar üretme → İmzalama → Doğrulama akışı otomatik test edilir
- ✅ **Docker test ortamı** — Tek komutla test ortamı ayağa kalkar
- ✅ **Kubernetes desteği** — `k8s/` klasöründe Minikube deployment dosyaları hazır

---

## 🧪 Testleri Çalıştırma

### Yöntem 1 — Docker ile (En Kolay, Python kurmana gerek yok)

[Docker Desktop](https://docker.com) kur, sonra:

```powershell
git checkout feature/kritik-eksikler
docker compose up --build
```

Tarayıcıda aç: **http://localhost:5000**

---

### Yöntem 2 — Python ile

```powershell
# Branch'e geç
git checkout feature/kritik-eksikler

# Sanal ortam oluştur
python -m venv venv

# Kütüphaneleri yükle
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Uygulamayı başlat
.\venv\Scripts\python.exe app.py
```

Tarayıcıda aç: **http://127.0.0.1:5001**

---

### Otomatik E2E Testleri

Uygulama çalışırken **yeni bir terminal** aç:

```powershell
# Playwright tarayıcısını yükle (ilk seferinde)
.\venv\Scripts\playwright.exe install chromium

# Testleri çalıştır (tarayıcı görünür açılır, izleyebilirsin)
.\venv\Scripts\python.exe -m pytest tests/test_e2e.py -v --headed --slowmo 1000
```

Beklenen sonuç:
```
tests/test_e2e.py::test_homepage_loads[chromium] PASSED       [ 50%]
tests/test_e2e.py::test_e2e_sign_and_verify[chromium] PASSED  [100%]
2 passed ✅
```

---

### Manuel Test Senaryoları

**Test için PEM dosyası oluşturmak:**
```powershell
.\venv\Scripts\python.exe -c "from cryptography.hazmat.primitives.asymmetric import rsa; from cryptography.hazmat.primitives import serialization; key = rsa.generate_private_key(public_exponent=65537, key_size=2048); open('test_private.pem','wb').write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())); open('test_public.pem','wb').write(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)); print('Hazir!')"
```

| Senaryo | Ne yapacaksın? | Beklenen Sonuç |
|---|---|---|
| **Normal akış** | `test_private.pem` ile metin imzala → `test_public.pem` ile doğrula | ✅ İmza Geçerli |
| **Büyük dosya** | 16 MB+ dosya yüklemeyi dene | ✅ Hata sayfası çıkar, çökmez |
| **Geçersiz imza** | Doğrularken metni 1 harf değiştir | ✅ İmza Geçersiz |
| **Boş dosya** | Key alanını boş bırak | ✅ Türkçe uyarı çıkar |

---

## 👥 Ekip

5 kişilik ekip tarafından geliştirilmektedir.

## 📄 Lisans

Bu proje eğitim amaçlıdır.
