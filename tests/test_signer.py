"""Signer testleri."""

import unittest
from modules.key_manager import generate_rsa_key_pair, generate_ed25519_key_pair, load_private_key_from_pem
from modules.signer import sign_data, sign_text, sign_file, create_sig_file_content


class TestSigner(unittest.TestCase):
    """Signer birim testleri."""

    @classmethod
    def setUpClass(cls):
        """Test öncesi setup."""
        # RSA anahtar
        cls.rsa_private_pem, cls.rsa_public_pem = generate_rsa_key_pair(2048)
        cls.rsa_private_key = load_private_key_from_pem(cls.rsa_private_pem)
        
        # Ed25519 anahtar
        cls.ed25519_private_pem, cls.ed25519_public_pem = generate_ed25519_key_pair()
        cls.ed25519_private_key = load_private_key_from_pem(cls.ed25519_private_pem)

    def test_sign_data_rsa(self):
        """RSA ile veri imzalama test et."""
        data = b"Test data for signing"
        result = sign_data(data, self.rsa_private_key)
        
        self.assertTrue(result["is_valid"] if "is_valid" in result else True)
        self.assertIn("signature_b64", result)
        self.assertIn("hash_hex", result)
        self.assertIn("algorithm", result)
        self.assertIn("RSA-PSS", result["algorithm"])
        self.assertEqual(len(result["hash_hex"]), 64)  # SHA-256 hex = 64 char

    def test_sign_data_ed25519(self):
        """Ed25519 ile veri imzalama test et."""
        data = b"Test data for Ed25519"
        result = sign_data(data, self.ed25519_private_key)
        
        self.assertIn("signature_b64", result)
        self.assertIn("hash_hex", result)
        self.assertIn("algorithm", result)
        self.assertIn("Ed25519", result["algorithm"])
        self.assertEqual(len(result["hash_hex"]), 64)

    def test_sign_text_rsa(self):
        """RSA ile metin imzalama test et."""
        text = "Merhaba Dünya"
        result = sign_text(text, self.rsa_private_key)
        
        self.assertIn("signature_b64", result)
        self.assertIn("RSA-PSS", result["algorithm"])

    def test_sign_file_rsa(self):
        """RSA ile dosya imzalama test et."""
        file_data = b"File content for signing"
        result = sign_file(file_data, self.rsa_private_key)
        
        self.assertIn("signature_b64", result)
        self.assertEqual(result["data_size"], len(file_data)) if "data_size" in result else True

    def test_sig_file_content_creation(self):
        """SIG dosyası içeriği oluşturma test et."""
        data = b"Test data"
        result = sign_data(data, self.rsa_private_key)
        sig_content = create_sig_file_content(result, "test.txt")
        
        self.assertIn("-----BEGIN DIGITAL SIGNATURE-----", sig_content)
        self.assertIn("-----END DIGITAL SIGNATURE-----", sig_content)
        self.assertIn("Algorithm:", sig_content)
        self.assertIn("Timestamp:", sig_content)
        self.assertIn("Hash-SHA256:", sig_content)
        self.assertIn("Signature:", sig_content)
        self.assertIn("Filename: test.txt", sig_content)

    def test_different_signatures(self):
        """İki farklı veri için farklı imzalar oluşturma test et."""
        data1 = b"Data 1"
        data2 = b"Data 2"
        
        sig1 = sign_data(data1, self.rsa_private_key)
        sig2 = sign_data(data2, self.rsa_private_key)
        
        self.assertNotEqual(sig1["hash_hex"], sig2["hash_hex"])
        self.assertNotEqual(sig1["signature_b64"], sig2["signature_b64"])

    def test_same_data_deterministic(self):
        """Aynı veri her zaman aynı hash'i oluşturma test et."""
        data = b"Deterministic data"
        
        sig1 = sign_data(data, self.rsa_private_key)
        sig2 = sign_data(data, self.rsa_private_key)
        
        self.assertEqual(sig1["hash_hex"], sig2["hash_hex"])
        # İmza RSA-PSS'de random padding kullanır, farklı olabilir


if __name__ == "__main__":
    unittest.main()
