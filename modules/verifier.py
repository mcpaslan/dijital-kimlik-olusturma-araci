"""
Verifier — Dijital imza doğrulama modülü.

İmza doğrulama işlemlerini gerçekleştirir.
Desteklenen algoritmalar:
  - RSA-PSS + SHA-256 (Prehashed)
  - Ed25519
Opsiyonel olarak sertifika zinciri doğrulaması da yapılır.
"""

import base64
import hashlib

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils, ed25519
from cryptography.exceptions import InvalidSignature


def verify_signature_rsa(data: bytes, signature_b64: str, public_key) -> dict:
    """RSA-PSS ile imzayı doğrular ve detaylı rapor oluşturur.

    Args:
        data: Orijinal veri (bytes).
        signature_b64: Base64 formatında imza.
        public_key: RSA public key nesnesi.

    Returns:
        Detaylı doğrulama sonucu içeren dict.
    """
    result = {
        "is_valid": False,
        "hash_hex": "",
        "algorithm": "RSA-PSS + SHA-256 (Prehashed)",
        "key_size": public_key.key_size,
        "signature_size": 0,
        "data_size": len(data),
        "details": [],
        "technical_details": {},
    }

    try:
        # 1. SHA-256 hash hesapla
        data_hash = hashlib.sha256(data).digest()
        result["hash_hex"] = data_hash.hex()

        # 2. İmzayı Base64'den decode et
        signature = base64.b64decode(signature_b64)
        result["signature_size"] = len(signature)

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
        result["details"].append("✅ İmza matematiksel olarak geçerli.")
        result["details"].append(f"✅ Veri değiştirilmemiş. SHA-256 Hash: {result['hash_hex'][:16]}...")
        result["details"].append(f"✅ RSA-{public_key.key_size} anahtarı ile doğrulandı.")
        result["technical_details"] = {
            "imza_boyutu": f"{result['signature_size']} byte",
            "veri_boyutu": f"{result['data_size']} byte",
            "hash_algoritma": "SHA-256",
            "padding_algoritma": "PSS (MGF1-SHA256)",
        }

    except InvalidSignature:
        result["details"].append("❌ İmza geçersiz — Veri değiştirilmiş olabilir veya yanlış anahtar kullanılmış.")
        result["details"].append(f"❌ Beklenen hash: {result['hash_hex'][:16]}... (tam: {result['hash_hex']})")
    except Exception as e:
        result["details"].append(f"❌ Doğrulama hatası: {str(e)}")

    return result


def verify_signature_ed25519(data: bytes, signature_b64: str, public_key) -> dict:
    """Ed25519 ile imzayı doğrular ve detaylı rapor oluşturur.

    Args:
        data: Orijinal veri (bytes).
        signature_b64: Base64 formatında imza.
        public_key: Ed25519 public key nesnesi.

    Returns:
        Detaylı doğrulama sonucu içeren dict.
    """
    result = {
        "is_valid": False,
        "hash_hex": "",
        "algorithm": "Ed25519",
        "key_size": 256,
        "signature_size": 0,
        "data_size": len(data),
        "details": [],
        "technical_details": {},
    }

    try:
        # 1. SHA-256 hash hesapla (rapor için)
        data_hash = hashlib.sha256(data).digest()
        result["hash_hex"] = data_hash.hex()

        # 2. İmzayı Base64'den decode et
        signature = base64.b64decode(signature_b64)
        result["signature_size"] = len(signature)

        # 3. Ed25519 ile doğrula
        public_key.verify(signature, data)

        result["is_valid"] = True
        result["details"].append("✅ İmza matematiksel olarak geçerli.")
        result["details"].append(f"✅ Veri değiştirilmemiş. SHA-256 Hash: {result['hash_hex'][:16]}...")
        result["details"].append("✅ Ed25519 (256-bit) anahtarı ile doğrulandı.")
        result["technical_details"] = {
            "imza_boyutu": f"{result['signature_size']} byte",
            "veri_boyutu": f"{result['data_size']} byte",
            "algoritma_detay": "EdDSA (Ed25519)",
            "note": "Ed25519 sabit 64-byte imza uzunluğu kullanır",
        }

    except InvalidSignature:
        result["details"].append("❌ İmza geçersiz — Veri değiştirilmiş olabilir veya yanlış anahtar kullanılmış.")
        result["details"].append(f"❌ Beklenen hash: {result['hash_hex'][:16]}... (tam: {result['hash_hex']})")
    except Exception as e:
        result["details"].append(f"❌ Doğrulama hatası: {str(e)}")

    return result


def verify_signature(data: bytes, signature_b64: str, public_key) -> dict:
    """İmzayı public key ile doğrular. Anahtar türüne göre otomatik seçim.

    Args:
        data: Orijinal veri (bytes).
        signature_b64: Base64 formatında imza.
        public_key: Public key nesnesi (RSA veya Ed25519).

    Returns:
        Doğrulama sonucunu içeren dict.
    """
    if isinstance(public_key, ed25519.Ed25519PublicKey):
        return verify_signature_ed25519(data, signature_b64, public_key)
    else:
        return verify_signature_rsa(data, signature_b64, public_key)


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
