"""
CA Manager — Demo Root CA oluşturma ve yönetimi.

Uygulama başlatıldığında:
  1. storage/ca/ca_key.pem ve ca_cert.pem var mı kontrol edilir
  2. Yoksa: RSA-4096 anahtar çifti + self-signed Root CA sertifikası oluşturulur
  3. Varsa: Mevcut CA yüklenir
"""

import os
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID


def _ensure_directory(path: str) -> None:
    """Dizin yoksa oluşturur."""
    os.makedirs(path, exist_ok=True)


def init_ca(ca_folder: str, ca_key_path: str, ca_cert_path: str, password: bytes = None) -> tuple:
    """Demo Root CA'yı başlatır.

    Args:
        ca_folder: CA dosyalarının saklanacağı dizin yolu.
        ca_key_path: CA private key dosya yolu.
        ca_cert_path: CA sertifika dosya yolu.
        password: CA özel anahtarını şifreleme parolası (bytes).

    Returns:
        (ca_key, ca_cert) tuple'ı.
    """
    _ensure_directory(ca_folder)

    if os.path.exists(ca_key_path) and os.path.exists(ca_cert_path):
        return _load_ca(ca_key_path, ca_cert_path, password)
    else:
        return _create_ca(ca_key_path, ca_cert_path, password)


def _create_ca(ca_key_path: str, ca_cert_path: str, password: bytes = None) -> tuple:
    """Yeni Demo Root CA oluşturur (RSA-4096, 10 yıl geçerli).

    Returns:
        (ca_key, ca_cert) tuple'ı.
    """
    # RSA-4096 anahtar çifti oluştur
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )

    # CA sertifikası için subject ve issuer (self-signed)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "TR"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Bilgisayar Guvenligi Projesi"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Demo Root CA"),
    ])

    now = datetime.now(timezone.utc)

    # Self-signed Root CA sertifikası oluştur
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=3650))  # 10 yıl
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=False,
                key_encipherment=False,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(
            ca_key,
            hashes.SHA256(),
            rsa_padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
        )
    )

    # Parola varsa şifrele, yoksa şifresiz kaydet (Zayıflık 2 çözümü)
    encryption_algorithm = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )

    # Dosyalara kaydet
    with open(ca_key_path, "wb") as f:
        f.write(
            ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption_algorithm,
            )
        )

    with open(ca_cert_path, "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    return ca_key, ca_cert


def _load_ca(ca_key_path: str, ca_cert_path: str, password: bytes = None) -> tuple:
    """Mevcut CA'yı dosyalardan yükler.

    Returns:
        (ca_key, ca_cert) tuple'ı.
    """
    with open(ca_key_path, "rb") as f:
        key_data = f.read()

    try:
        ca_key = serialization.load_pem_private_key(key_data, password=password)
    except TypeError as e:
        if "private key is not encrypted" in str(e).lower() or "password was given" in str(e).lower():
            ca_key = serialization.load_pem_private_key(key_data, password=None)
        else:
            raise e

    with open(ca_cert_path, "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())

    return ca_key, ca_cert


def get_ca_cert_info(ca_cert) -> dict:
    """CA sertifika bilgilerini okunabilir formatta döndürür."""
    return {
        "subject": ca_cert.subject.rfc4514_string(),
        "issuer": ca_cert.issuer.rfc4514_string(),
        "serial_number": format(ca_cert.serial_number, "X"),
        "not_valid_before": ca_cert.not_valid_before_utc.isoformat(),
        "not_valid_after": ca_cert.not_valid_after_utc.isoformat(),
        "algorithm": ca_cert.signature_algorithm_oid._name,
    }
