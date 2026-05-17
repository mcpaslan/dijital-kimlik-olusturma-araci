"""
Certificate Manager — X.509 sertifika üretme ve yönetimi.

Kullanıcı sertifikaları Demo Root CA tarafından imzalanır.
Desteklenen CA algoritmaları: RSA-PSS, Ed25519
Sertifika bilgilerini parse edip okunabilir formatta gösterir.
"""

from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, ed25519
from cryptography.x509.oid import NameOID


def create_user_certificate(
    common_name: str,
    email: str,
    public_key_pem: bytes,
    ca_key,
    ca_cert,
    validity_days: int = 365,
) -> bytes:
    """Kullanıcı için X.509 sertifika oluşturur ve CA ile imzalar.

    CA key type'ına göre otomatik olarak uygun imzalama algoritması seçilir.

    Args:
        common_name: Kullanıcı adı (CN).
        email: Kullanıcı e-posta adresi.
        public_key_pem: Kullanıcının public key'i (PEM bytes).
        ca_key: CA private key nesnesi (RSA veya Ed25519).
        ca_cert: CA sertifika nesnesi.
        validity_days: Sertifika geçerlilik süresi (gün).

    Returns:
        Sertifika PEM formatında (bytes).
    """
    # Public key'i yükle
    user_public_key = serialization.load_pem_public_key(public_key_pem)

    # Sertifika subject bilgileri
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "TR"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
    ])

    now = datetime.now(timezone.utc)

    # Sertifika oluştur
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(user_public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=validity_days))
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=False,
                content_commitment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(user_public_key),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(
                ca_cert.public_key()
            ),
            critical=False,
        )
    )

    # CA key type'ına göre imzala
    if isinstance(ca_key, ed25519.Ed25519PrivateKey):
        # Ed25519 ile imzala
        cert = builder.sign(ca_key, hashes.SHA256())
    else:
        # RSA-PSS ile imzala
        cert = builder.sign(
            ca_key,
            hashes.SHA256(),
            rsa_padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
        )

    return cert.public_bytes(serialization.Encoding.PEM)


def parse_certificate(cert_pem: bytes) -> dict:
    """Sertifika PEM verisini okunabilir bilgilere dönüştürür.

    Args:
        cert_pem: PEM formatında sertifika verisi.

    Returns:
        Sertifika bilgilerini içeren dict.
    """
    cert = x509.load_pem_x509_certificate(cert_pem)

    # Subject alanlarını çıkar
    subject_attrs = {}
    for attr in cert.subject:
        subject_attrs[attr.oid._name] = attr.value

    # Issuer alanlarını çıkar
    issuer_attrs = {}
    for attr in cert.issuer:
        issuer_attrs[attr.oid._name] = attr.value

    # Public key boyutunu al (Ed25519 için 256, RSA için büyük sayılar)
    public_key = cert.public_key()
    try:
        key_size = public_key.key_size
    except AttributeError:
        # Ed25519 için key_size özelliği yok, 256 bit olarak bili
        key_size = 256

    return {
        "subject": cert.subject.rfc4514_string(),
        "subject_cn": subject_attrs.get("commonName", "N/A"),
        "subject_email": subject_attrs.get("emailAddress", "N/A"),
        "issuer": cert.issuer.rfc4514_string(),
        "issuer_cn": issuer_attrs.get("commonName", "N/A"),
        "serial_number": format(cert.serial_number, "X"),
        "not_valid_before": cert.not_valid_before_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "not_valid_after": cert.not_valid_after_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "not_valid_before_dt": cert.not_valid_before_utc,
        "not_valid_after_dt": cert.not_valid_after_utc,
        "algorithm": cert.signature_algorithm_oid._name,
        "is_expired": datetime.now(timezone.utc) > cert.not_valid_after_utc,
        "version": cert.version.name,
        "public_key_size": key_size,
    }


def verify_certificate_chain(cert_pem: bytes, ca_cert) -> dict:
    """Sertifikanın CA tarafından imzalanıp imzalanmadığını kontrol eder.

    CA key type'ına göre otomatik olarak uygun doğrulama yöntemi seçilir.

    Args:
        cert_pem: Doğrulanacak sertifika (PEM bytes).
        ca_cert: CA sertifika nesnesi.

    Returns:
        Doğrulama sonucunu içeren dict.
    """
    cert = x509.load_pem_x509_certificate(cert_pem)
    now = datetime.now(timezone.utc)

    result = {
        "is_valid": False,
        "ca_verified": False,
        "is_expired": False,
        "details": [],
    }

    # 1. Sertifika süresi kontrolü
    if now > cert.not_valid_after_utc:
        result["is_expired"] = True
        result["details"].append("❌ Sertifika süresi dolmuş.")
    elif now < cert.not_valid_before_utc:
        result["details"].append("❌ Sertifika henüz geçerli değil.")
    else:
        result["details"].append("✅ Sertifika geçerlilik süresi aktif.")

    # 2. CA imzası doğrulama - CA key type'ına göre seç
    ca_public_key = ca_cert.public_key()
    try:
        if isinstance(ca_public_key, ed25519.Ed25519PublicKey):
            # Ed25519 ile doğrula
            ca_public_key.verify(cert.signature, cert.tbs_certificate_bytes)
        else:
            # RSA-PSS ile doğrula
            ca_public_key.verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                cert.signature_hash_algorithm,
            )
        result["ca_verified"] = True
        result["details"].append("✅ Sertifika güvenilir CA tarafından imzalanmış.")
    except Exception:
        result["details"].append("❌ Sertifika güvenilir CA tarafından imzalanmamış.")

    # Genel sonuç
    result["is_valid"] = result["ca_verified"] and not result["is_expired"]

    return result
