"""
Key Manager — RSA ve Ed25519 anahtar çifti oluşturma.

Desteklenen algoritmalar:
  - RSA: 2048 ve 4096 bit
  - Ed25519: Sabit 256-bit

Private key kullanıcıya PEM dosyası olarak indirilir,
sunucuda yalnızca public key saklanır.
"""

from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import serialization


def generate_rsa_key_pair(key_size: int = 2048, password: bytes = None) -> tuple:
    """RSA anahtar çifti oluşturur.

    Args:
        key_size: Anahtar boyutu (2048 veya 4096).
        password: Özel anahtarı şifrelemek için şifre bytes (opsiyonel).

    Returns:
        (private_key_pem, public_key_pem) — bytes tuple'ı (PEM formatında).

    Raises:
        ValueError: Geçersiz anahtar boyutu.
    """
    if key_size not in (2048, 4096):
        raise ValueError("Anahtar boyutu 2048 veya 4096 olmalıdır.")

    # RSA anahtar çifti oluştur
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    # Parola varsa şifrele, yoksa şifresiz kaydet
    encryption_algorithm = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )

    # Private key → PEM (kullanıcıya indirilecek)
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm,
    )

    # Public key → PEM (sunucuda saklanacak)
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_key_pem, public_key_pem


def load_private_key_from_pem(pem_data: bytes, password: bytes = None):
    """PEM formatındaki private key'i yükler.

    Args:
        pem_data: PEM formatında private key verisi.
        password: Özel anahtarı çözmek için şifre bytes (opsiyonel).

    Returns:
        RSAPrivateKey nesnesi.
    """
    return serialization.load_pem_private_key(pem_data, password=password)


def load_public_key_from_pem(pem_data: bytes):
    """PEM formatındaki public key'i yükler.

    Args:
        pem_data: PEM formatında public key verisi.

    Returns:
        RSAPublicKey nesnesi.
    """
    return serialization.load_pem_public_key(pem_data)


def generate_ed25519_key_pair() -> tuple:
    """Ed25519 anahtar çifti oluşturur.

    Ed25519 her zaman 256-bit'tir.

    Returns:
        (private_key_pem, public_key_pem) — bytes tuple'ı (PEM formatında).
    """
    # Ed25519 anahtar çifti oluştur
    private_key = ed25519.Ed25519PrivateKey.generate()

    # Private key → PEM (şifresiz, kullanıcıya indirilecek)
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Public key → PEM (sunucuda saklanacak)
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_key_pem, public_key_pem
