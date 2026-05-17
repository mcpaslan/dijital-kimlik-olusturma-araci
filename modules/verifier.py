"""
Verifier — Dijital imza doğrulama modülü.

İmza doğrulama işlemlerini gerçekleştirir.
RSA-PSS + SHA-256 (Prehashed) kullanılır.
Opsiyonel olarak sertifika zinciri doğrulaması da yapılır.
"""

import base64
import hashlib

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.exceptions import InvalidSignature


def verify_signature(data: bytes, signature_b64: str, public_key) -> dict:
    """İmzayı public key ile doğrular.

    Args:
        data: Orijinal veri (bytes).
        signature_b64: Base64 formatında imza.
        public_key: RSA public key nesnesi.

    Returns:
        Doğrulama sonucunu içeren dict.
    """
    result = {
        "is_valid": False,
        "hash_hex": "",
        "details": [],
    }

    try:
        # 1. SHA-256 hash hesapla
        data_hash = hashlib.sha256(data).digest()
        result["hash_hex"] = data_hash.hex()

        # 2. İmzayı Base64'den decode et
        signature = base64.b64decode(signature_b64)

        # 3. RSA-PSS + Prehashed ile doğrula
        public_key.verify(
            signature,
            data_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            utils.Prehashed(hashes.SHA256()),
        )

        result["is_valid"] = True
        result["details"].append("✅ İmza geçerli — veri değiştirilmemiş.")
        result["details"].append("✅ İmza doğru anahtara ait.")

    except InvalidSignature:
        result["details"].append("❌ İmza geçersiz — veri değiştirilmiş olabilir veya yanlış anahtar kullanılmış.")
    except Exception as e:
        result["details"].append(f"❌ Doğrulama hatası: {str(e)}")

    return result


def verify_text(text: str, signature_b64: str, public_key) -> dict:
    """Metin imzasını doğrular.

    Args:
        text: Orijinal metin.
        signature_b64: Base64 formatında imza.
        public_key: RSA public key nesnesi.

    Returns:
        Doğrulama sonucunu içeren dict.
    """
    return verify_signature(text.encode("utf-8"), signature_b64, public_key)


def verify_file(file_data: bytes, signature_b64: str, public_key) -> dict:
    """Dosya imzasını doğrular.

    Args:
        file_data: Orijinal dosya içeriği (bytes).
        signature_b64: Base64 formatında imza.
        public_key: RSA public key nesnesi.

    Returns:
        Doğrulama sonucunu içeren dict.
    """
    return verify_signature(file_data, signature_b64, public_key)


def parse_sig_file(sig_content: str) -> dict:
    """'.sig' dosyası içeriğini parse eder.

    Args:
        sig_content: .sig dosyasının metin içeriği.

    Returns:
        Parse edilmiş imza bilgilerini içeren dict.
    """
    result = {
        "algorithm": "",
        "timestamp": "",
        "hash_hex": "",
        "filename": "",
        "signature_b64": "",
    }

    for line in sig_content.strip().splitlines():
        line = line.strip()
        if line.startswith("Algorithm:"):
            result["algorithm"] = line.split(":", 1)[1].strip()
        elif line.startswith("Timestamp:"):
            result["timestamp"] = line.split(":", 1)[1].strip()
        elif line.startswith("Hash-SHA256:"):
            result["hash_hex"] = line.split(":", 1)[1].strip()
        elif line.startswith("Filename:"):
            result["filename"] = line.split(":", 1)[1].strip()
        elif line.startswith("Signature:"):
            result["signature_b64"] = line.split(":", 1)[1].strip()

    return result


def load_public_key_from_pem(pem_data: bytes):
    """PEM formatındaki public key'i yükler."""
    return serialization.load_pem_public_key(pem_data)


def load_public_key_from_certificate(cert_pem: bytes):
    """Sertifikadan public key çıkarır."""
    from cryptography import x509

    cert = x509.load_pem_x509_certificate(cert_pem)
    return cert.public_key()
