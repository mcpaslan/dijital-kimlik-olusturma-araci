"""
Dijital İmza Oluşturma ve Doğrulama Aracı — Flask Uygulaması.

Bilgisayar güvenliği dersi projesi.
RSA-PSS + SHA-256 ile dijital imza oluşturma, doğrulama ve basit PKI simülasyonu.
"""

import os
from flask import Flask, render_template
from sqlalchemy import text

from config import Config
from models.database import db
from modules.ca_manager import init_ca, get_ca_cert_info


def create_app(test=False, db_path=None):
    """Flask uygulama fabrikası."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Test mode
    if test:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_path or "sqlite:///:memory:"
        app.config["TESTING"] = True

    # Gerekli dizinleri oluştur
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["SIGNATURES_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Veritabanını başlat
    db.init_app(app)

    with app.app_context():
        # Tabloları oluştur
        db.create_all()
        
        # Migration: Eksik column'ları ekle (otomatik kontrol)
        if not test:
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                user_columns = [col["name"] for col in inspector.get_columns("users")]
                cert_columns = [col["name"] for col in inspector.get_columns("certificates")]
                
                # Users tablosuna key_algorithm eklenmiş mi kontrol et
                if "key_algorithm" not in user_columns:
                    db.session.execute(text("ALTER TABLE users ADD COLUMN key_algorithm VARCHAR(20) DEFAULT 'RSA'"))
                    db.session.commit()
                    print("✅ users tablosuna key_algorithm sütunu eklendi")
                
                # Certificates tablosuna revoke alanları eklenmiş mi kontrol et
                if "revoke_reason" not in cert_columns:
                    db.session.execute(text("ALTER TABLE certificates ADD COLUMN revoke_reason VARCHAR(255)"))
                    db.session.execute(text("ALTER TABLE certificates ADD COLUMN revoked_at DATETIME"))
                    db.session.commit()
                    print("✅ certificates tablosuna revoke alanları eklendi")
            except Exception as e:
                print(f"⚠️ Migration hatası (ignorable): {e}")

        # Demo Root CA'yı başlat
        ca_key, ca_cert = init_ca(
            ca_folder=app.config["CA_FOLDER"],
            ca_key_path=app.config["CA_KEY_PATH"],
            ca_cert_path=app.config["CA_CERT_PATH"],
        )
        app.config["CA_KEY"] = ca_key
        app.config["CA_CERT"] = ca_cert

        ca_info = get_ca_cert_info(ca_cert)
        print(f"✅ Demo Root CA aktif: {ca_info['subject']}")

    # Blueprint'leri kaydet
    from routes.keys import keys_bp
    from routes.certificates import certs_bp
    from routes.signing import signing_bp
    from routes.verification import verification_bp

    app.register_blueprint(keys_bp)
    app.register_blueprint(certs_bp)
    app.register_blueprint(signing_bp)
    app.register_blueprint(verification_bp)

    # Ana sayfa route'u
    @app.route("/")
    def index():
        ca_info = get_ca_cert_info(app.config["CA_CERT"])
        return render_template("index.html", ca_info=ca_info)

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template("error.html", title="Dosya Çok Büyük", message="Yüklediğiniz dosya izin verilen sınırı aşıyor (Maksimum 16 MB)."), 413

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
