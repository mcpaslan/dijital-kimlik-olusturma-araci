"""
Dijital İmza Oluşturma ve Doğrulama Aracı — Flask Uygulaması.

Bilgisayar güvenliği dersi projesi.
RSA-PSS + SHA-256 ile dijital imza oluşturma, doğrulama ve basit PKI simülasyonu.
"""

import os
from flask import Flask, render_template

from config import Config
from models.database import db
from modules.ca_manager import init_ca, get_ca_cert_info


def create_app():
    """Flask uygulama fabrikası."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Gerekli dizinleri oluştur
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["SIGNATURES_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Veritabanını başlat
    db.init_app(app)

    with app.app_context():
        # Tabloları oluştur
        db.create_all()

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

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5001)
