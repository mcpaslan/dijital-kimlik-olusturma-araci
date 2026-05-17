"""Verifier testleri."""

import unittest
from modules.key_manager import generate_rsa_key_pair, generate_ed25519_key_pair, load_private_key_from_pem, load_public_key_from_pem
from modules.signer import sign_data, sign_text, sign_file
from modules.verifier import verify_signature, verify_text, verify_file, parse_sig_file


class TestVerifier(unittest.TestCase):
    """Verifier birim testleri."""

    @classmethod
    def setUpClass(cls):
        """Test öncesi setup."""
        # RSA anahtar
        cls.rsa_private_pem, cls.rsa_public_pem = generate_rsa_key_pair(2048)
        cls.rsa_private_key = load_private_key_from_pem(cls.rsa_private_pem)
        cls.rsa_public_key = load_public_key_from_pem(cls.rsa_public_pem)
        
        # Ed25519 anahtar
        cls.ed25519_private_pem, cls.ed25519_public_pem = generate_ed25519_key_pair()
        cls.ed25519_private_key = load_private_key_from_pem(cls.ed25519_private_pem)
        cls.ed25519_public_key = load_public_key_from_pem(cls.ed25519_public_pem)

    def test_verify_valid_rsa_signature(self):
        """Geçerli RSA imzasını doğrulama test et."""
        data = b"Test data"
        sig_result = sign_data(data, self.rsa_private_key)
        
        result = verify_signature(data, sig_result["signature_b64"], self.rsa_public_key)
        
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["hash_hex"], sig_result["hash_hex"])
        self.assertIn("✅", "".join(result["details"]))

    def test_verify_valid_ed25519_signature(self):
        """Geçerli Ed25519 imzasını doğrulama test et."""
        data = b"Test data for Ed25519"
        sig_result = sign_data(data, self.ed25519_private_key)
        
        result = verify_signature(data, sig_result["signature_b64"], self.ed25519_public_key)
        
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["hash_hex"], sig_result["hash_hex"])

    def test_verify_tampered_data_rsa(self):
        """Değiştirilmiş verinin imzası doğrulamayı test et (RSA)."""
        data = b"Original data"
        sig_result = sign_data(data, self.rsa_private_key)
        
        tampered_data = b"Tampered data"
        result = verify_signature(tampered_data, sig_result["signature_b64"], self.rsa_public_key)
        
        self.assertFalse(result["is_valid"])
        self.assertIn("❌", "".join(result["details"]))

    def test_verify_tampered_data_ed25519(self):
        """Değiştirilmiş verinin imzası doğrulamayı test et (Ed25519)."""
        data = b"Original data"
        sig_result = sign_data(data, self.ed25519_private_key)
        
        tampered_data = b"Tampered data"
        result = verify_signature(tampered_data, sig_result["signature_b64"], self.ed25519_public_key)
        
        self.assertFalse(result["is_valid"])

    def test_verify_invalid_signature_format(self):
        """Geçersiz imza formatını doğrulama test et."""
        data = b"Test data"
        invalid_signature = "not-a-valid-base64-signature!!!"
        
        result = verify_signature(data, invalid_signature, self.rsa_public_key)
        
        self.assertFalse(result["is_valid"])
        self.assertIn("❌", "".join(result["details"]))

    def test_verify_text_rsa(self):
        """Metin imzasını doğrulama test et (RSA)."""
        text = "Merhaba Dünya"
        sig_result = sign_text(text, self.rsa_private_key)
        
        result = verify_text(text, sig_result["signature_b64"], self.rsa_public_key)
        
        self.assertTrue(result["is_valid"])

    def test_verify_file_ed25519(self):
        """Dosya imzasını doğrulama test et (Ed25519)."""
        file_data = b"File content"
        sig_result = sign_file(file_data, self.ed25519_private_key)
        
        result = verify_file(file_data, sig_result["signature_b64"], self.ed25519_public_key)
        
        self.assertTrue(result["is_valid"])

    def test_parse_sig_file(self):
        """SIG dosyasını parse etme test et."""
        sig_content = """-----BEGIN DIGITAL SIGNATURE-----
Algorithm: RSA-PSS + SHA-256
Timestamp: 2026-05-17 10:30:00 UTC
Hash-SHA256: abcd1234
Filename: test.txt
Signature: base64encodedsignature
-----END DIGITAL SIGNATURE-----"""
        
        result = parse_sig_file(sig_content)
        
        self.assertEqual(result["algorithm"], "RSA-PSS + SHA-256")
        self.assertEqual(result["hash_hex"], "abcd1234")
        self.assertEqual(result["filename"], "test.txt")
        self.assertEqual(result["signature_b64"], "base64encodedsignature")

    def test_verify_detailed_report(self):
        """Detaylı doğrulama raporunu test et."""
        data = b"Test data"
        sig_result = sign_data(data, self.rsa_private_key)
        result = verify_signature(data, sig_result["signature_b64"], self.rsa_public_key)
        
        self.assertIn("algorithm", result)
        self.assertIn("key_size", result)
        self.assertIn("signature_size", result)
        self.assertIn("data_size", result)
        self.assertIn("technical_details", result)
        
        self.assertEqual(result["key_size"], 2048)
        self.assertEqual(result["data_size"], len(data))


if __name__ == "__main__":
    unittest.main()
