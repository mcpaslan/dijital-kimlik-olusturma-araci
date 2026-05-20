import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Uygulama konfigürasyon ayarları."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # SQLite veritabanı
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dosya yükleme ayarları
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "storage", "uploads")
    SIGNATURES_FOLDER = os.path.join(BASE_DIR, "storage", "signatures")

    # CA dizini
    CA_FOLDER = os.path.join(BASE_DIR, "storage", "ca")
    CA_KEY_PATH = os.path.join(CA_FOLDER, "ca_key.pem")
    CA_CERT_PATH = os.path.join(CA_FOLDER, "ca_cert.pem")

    # İzin verilen dosya uzantıları
    ALLOWED_EXTENSIONS = {"pdf", "txt", "doc", "docx", "png", "jpg", "xml", "json"}

    # CA Şifreleme Parolası (Zayıflık 2 Çözümü)
    CA_PASSWORD = os.environ.get("CA_PASSWORD", "SuperSecureRootCAPassword2026!")

