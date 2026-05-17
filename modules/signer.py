"""
Signer — Dijital imzalama modülü.

Metin ve dosya imzalama işlemlerini gerçekleştirir.
Desteklenen algoritmalar:
  - RSA-PSS + SHA-256 (Prehashed)
  - Ed25519
"""

import base64
import hashlib
from datetime import datetime, timezone

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, utils, ed25519


def compute_sha256_hash(data: bytes) -> bytes:
    """Verinin SHA-256 hash özetini hesaplar.

    Args:
        data: Hash'lenecek veri (bytes).

    Returns:
        32 byte SHA-256 hash değeri.
    """
    return hashlib.sha256(data).digest()


def sign_data_rsa(data: bytes, private_key) -> dict:
    """Veriyi RSA-PSS ile imzalar.

    Akış: data → SHA-256 hash → Prehashed(SHA256) → RSA-PSS imza

    Args:
        data: İmzalanacak veri (metin veya dosya içeriği, bytes).
        private_key: RSA private key nesnesi.

    Returns:
        İmza bilgilerini içeren dict.
    """
    # 1. SHA-256 hash hesapla
    data_hash = compute_sha256_hash(data)

    # 2. Prehashed kullanarak imzala (çift hash'lemeyi önler)
    signature = private_key.sign(
        data_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        utils.Prehashed(hashes.SHA256()),
    )

    return {
        "signature_b64": base64.b64encode(signature).decode("utf-8"),
        "hash_hex": data_hash.hex(),
        "algorithm": "RSA-PSS + SHA-256 (Prehashed)",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


def sign_data_ed25519(data: bytes, private_key) -> dict:
    """Veriyi Ed25519 ile imzalar.

    Args:
        data: İmzalanacak veri (metin veya dosya içeriği, bytes).
        private_key: Ed25519 private key nesnesi.

    Returns:
        İmza bilgilerini içeren dict.
    """
    # Ed25519 doğrudan veriyi imzalar (hash hesaplamıyor)
    signature = private_key.sign(data)
    data_hash = compute_sha256_hash(data)

    return {
        "signature_b64": base64.b64encode(signature).decode("utf-8"),
        "hash_hex": data_hash.hex(),
        "algorithm": "Ed25519",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


def sign_data(data: bytes, private_key) -> dict:
    """Veriyi imzalar. Anahtar türüne göre otomatik algoritma seçer.

    Args:
        data: İmzalanacak veri (metin veya dosya içeriği, bytes).
        private_key: Private key nesnesi (RSA veya Ed25519).

    Returns:
        İmza bilgilerini içeren dict:
          - signature_b64: İmza (Base64)
          - hash_hex: SHA-256 hash (hex)
          - algorithm: Kullanılan algoritma
          - timestamp: İmzalama zamanı
    """
    if isinstance(private_key, ed25519.Ed25519PrivateKey):
        return sign_data_ed25519(data, private_key)
    else:
        return sign_data_rsa(data, private_key)


def sign_text(text: str, private_key) -> dict:
    """Metin verisini imzalar.

    Args:
        text: İmzalanacak metin.
        private_key: RSA private key nesnesi.

    Returns:
        İmza bilgilerini içeren dict.
    """
    return sign_data(text.encode("utf-8"), private_key)


def sign_file(file_data: bytes, private_key) -> dict:
    """Dosya verisini imzalar.

    Args:
        file_data: Dosya içeriği (bytes).
        private_key: RSA private key nesnesi.

    Returns:
        İmza bilgilerini içeren dict.
    """
    return sign_data(file_data, private_key)


def create_sig_file_content(signature_result: dict, filename: str = "") -> str:
    """İndirilebilir .sig dosyası içeriği oluşturur.

    Args:
        signature_result: sign_data fonksiyonunun döndürdüğü dict.
        filename: İmzalanan dosyanın adı (opsiyonel).

    Returns:
        .sig dosyası içeriği (string).
    """
    lines = [
        "-----BEGIN DIGITAL SIGNATURE-----",
        f"Algorithm: {signature_result['algorithm']}",
        f"Timestamp: {signature_result['timestamp']}",
        f"Hash-SHA256: {signature_result['hash_hex']}",
    ]
    if filename:
        lines.append(f"Filename: {filename}")
    lines.append(f"Signature: {signature_result['signature_b64']}")
    lines.append("-----END DIGITAL SIGNATURE-----")

    return "\n".join(lines)
