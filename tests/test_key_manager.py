"""Key Manager testleri."""

import unittest
from modules.key_manager import (
    generate_rsa_key_pair,
    generate_ed25519_key_pair,
    load_private_key_from_pem,
    load_public_key_from_pem,
)
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519


class TestKeyManager(unittest.TestCase):
    """Key Manager birim testleri."""

    def test_generate_rsa_2048(self):
        """RSA-2048 anahtar çifti üretmesi test et."""
        private_pem, public_pem = generate_rsa_key_pair(2048)
        
        self.assertIsNotNone(private_pem)
        self.assertIsNotNone(public_pem)
        self.assertIn(b"BEGIN PRIVATE KEY", private_pem)
        self.assertIn(b"BEGIN PUBLIC KEY", public_pem)
        
        # Key'leri yükle ve kontrol et
        private_key = load_private_key_from_pem(private_pem)
        public_key = load_public_key_from_pem(public_pem)
        
        self.assertIsInstance(private_key, rsa.RSAPrivateKey)
        self.assertEqual(private_key.key_size, 2048)
        self.assertEqual(public_key.key_size, 2048)

    def test_generate_rsa_4096(self):
        """RSA-4096 anahtar çifti üretmesi test et."""
        private_pem, public_pem = generate_rsa_key_pair(4096)
        
        private_key = load_private_key_from_pem(private_pem)
        self.assertEqual(private_key.key_size, 4096)

    def test_generate_rsa_invalid_size(self):
        """Geçersiz RSA anahtar boyutu hatası test et."""
        with self.assertRaises(ValueError):
            generate_rsa_key_pair(1024)
        
        with self.assertRaises(ValueError):
            generate_rsa_key_pair(8192)

    def test_generate_ed25519(self):
        """Ed25519 anahtar çifti üretmesi test et."""
        private_pem, public_pem = generate_ed25519_key_pair()
        
        self.assertIsNotNone(private_pem)
        self.assertIsNotNone(public_pem)
        self.assertIn(b"BEGIN PRIVATE KEY", private_pem)
        self.assertIn(b"BEGIN PUBLIC KEY", public_pem)
        
        # Key'leri yükle ve kontrol et
        private_key = load_private_key_from_pem(private_pem)
        public_key = load_public_key_from_pem(public_pem)
        
        self.assertIsInstance(private_key, ed25519.Ed25519PrivateKey)
        self.assertIsInstance(public_key, ed25519.Ed25519PublicKey)

    def test_load_invalid_pem(self):
        """Geçersiz PEM dosyası yüklemesi test et."""
        invalid_pem = b"This is not a valid PEM"
        
        with self.assertRaises(Exception):
            load_private_key_from_pem(invalid_pem)
        
        with self.assertRaises(Exception):
            load_public_key_from_pem(invalid_pem)


if __name__ == "__main__":
    unittest.main()
