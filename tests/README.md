# Birim Testleri (Unit Tests)

Dijital Kimlik Oluşturma Aracının birim testleri.

## Test Dosyaları

### 1. **test_key_manager.py**
- RSA-2048/4096 anahtar üretimi
- Ed25519 anahtar üretimi
- Geçersiz anahtar boyutları
- PEM dosyası yükleme

### 2. **test_signer.py**
- RSA-PSS imzalama
- Ed25519 imzalama
- Metin ve dosya imzalama
- SIG dosyası oluşturma
- İmza deterministik testi

### 3. **test_verifier.py**
- Geçerli RSA imzası doğrulama
- Geçerli Ed25519 imzası doğrulama
- Değiştirilmiş veri tespiti
- Geçersiz imza formatı tespiti
- Detaylı doğrulama raporları
- SIG dosyası parse etme

### 4. **test_certificate_manager.py**
- RSA ile sertifika oluşturma
- Ed25519 ile sertifika oluşturma
- Sertifika parsing
- Sertifika zinciri doğrulama
- Geçerlilik tarihleri
- Anahtar boyutları

### 5. **test_routes.py** (Integration Tests)
- Index sayfası
- Anahtar oluşturma formu
- RSA anahtar oluşturma (POST)
- Ed25519 anahtar oluşturma (POST)
- Anahtar listesi
- Sertifika ve imza sayfaları

## Testleri Çalıştırma

### Gereklilikler
```bash
pip install pytest pytest-cov
```

### Tüm Testleri Çalıştırma
```bash
python -m pytest tests/ -v
```

### Belirli bir test dosyasını çalıştırma
```bash
python -m pytest tests/test_key_manager.py -v
python -m pytest tests/test_signer.py -v
python -m pytest tests/test_verifier.py -v
python -m pytest tests/test_certificate_manager.py -v
python -m pytest tests/test_routes.py -v
```

### Coverage Raporu
```bash
python -m pytest tests/ --cov=modules --cov=routes --cov=models --cov-report=html
```

Coverage raporunu `htmlcov/index.html` dosyasında görebilirsiniz.

### Belirli bir test çalıştırma
```bash
python -m pytest tests/test_key_manager.py::TestKeyManager::test_generate_rsa_2048 -v
```

## Test İstatistikleri

- **Toplam Test Sayısı**: 25+
- **Kapsanan Modüller**: key_manager, signer, verifier, certificate_manager, routes
- **Algoritma Kapsamı**: RSA (2048/4096), Ed25519

## Test Senaryoları

✅ **Anahtar Yönetimi**
- RSA anahtar çiftleri (2048 ve 4096 bit)
- Ed25519 anahtar çiftleri
- PEM format yükleme/dump
- Geçersiz boyut hataları

✅ **İmzalama**
- RSA-PSS + SHA-256
- Ed25519
- Metin ve dosya imzalama
- İmza metadata'sı

✅ **Doğrulama**
- İmza doğruluğu
- Veri bütünlüğü
- Yanlış anahtar tespiti
- Detaylı raporlar

✅ **Sertifikalandırma**
- X.509 sertifika oluşturma
- CA zinciri doğrulama
- Geçerlilik tarihleri
- Sertifika parsing

✅ **Web Routes**
- Form gösterilimi
- POST istekleri
- Veritabanı kayıtları
- Sayfa navigasyonu

## Debugging Testi

Belirli bir test'i verbose mode'da çalıştırma:
```bash
python -m pytest tests/test_key_manager.py::TestKeyManager::test_generate_rsa_2048 -vv -s
```

Veya unittest kullanarak:
```bash
python -m unittest tests.test_key_manager.TestKeyManager.test_generate_rsa_2048 -v
```

## Notlar

- Tests, geçici SQLite veritabanı kullanır
- Integration tests'ler Flask test client kullanır
- Ed25519 ve RSA testleri paralel çalışabilir
- Her test kendi setup/teardown yapısına sahiptir
