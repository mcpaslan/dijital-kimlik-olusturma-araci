"""
Veritabanı modelleri — SQLAlchemy ile SQLite.

Tablolar:
  - User: Kullanıcı bilgileri ve public key
  - Certificate: X.509 sertifika metadata
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class User(db.Model):
    """Kullanıcı ve anahtar bilgileri.

    Private key sunucuda saklanmaz; yalnızca public key,
    sertifika ve metadata tutulur.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    common_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    public_key_pem = db.Column(db.Text, nullable=False)
    key_size = db.Column(db.Integer, nullable=False, default=2048)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # İlişki: Bir kullanıcının birden fazla sertifikası olabilir
    certificates = db.relationship("Certificate", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.common_name} ({self.email})>"


class Certificate(db.Model):
    """X.509 sertifika metadata bilgileri."""

    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    serial_number = db.Column(db.String(255), unique=True, nullable=False)
    certificate_pem = db.Column(db.Text, nullable=False)
    issuer = db.Column(db.String(255), nullable=False)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    algorithm = db.Column(db.String(50), nullable=False, default="RSA-PSS-SHA256")
    is_revoked = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Certificate SN:{self.serial_number} for User:{self.user_id}>"
