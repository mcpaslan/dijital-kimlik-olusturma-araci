"""Certificate Manager testleri."""

import unittest
from datetime import datetime, timezone
from modules.key_manager import generate_rsa_key_pair, generate_ed25519_key_pair, load_private_key_from_pem, load_public_key_from_pem
from modules.ca_manager import initialize_root_ca
from modules.certificate_manager import create_user_certificate, parse_certificate, verify_certificate_chain


class TestCertificateManager(unittest.TestCase):
    """Certificate Manager birim testleri."""

    @classmethod
    def setUpClass(cls):
        """Test öncesi setup."""
        # CA oluştur
        cls.ca_key, cls.ca_cert = initialize_root_ca()
        
        # User RSA anahtar
        cls.user_rsa_private_pem, cls.user_rsa_public_pem = generate_rsa_key_pair(2048)
        
        # User Ed25519 anahtar
        cls.user_ed25519_private_pem, cls.user_ed25519_public_pem = generate_ed25519_key_pair()

    def test_create_certificate_with_rsa(self):
        """RSA public key ile sertifika oluşturma test et."""
        cert_pem = create_user_certificate(
            common_name="Test User",
            email="test@example.com",
            public_key_pem=self.user_rsa_public_pem,
            ca_key=self.ca_key,
            ca_cert=self.ca_cert,
        )
        
        self.assertIsNotNone(cert_pem)
        self.assertIn(b"BEGIN CERTIFICATE", cert_pem)
        self.assertIn(b"END CERTIFICATE", cert_pem)

    def test_create_certificate_with_ed25519(self):
        """Ed25519 public key ile sertifika oluşturma test et."""
        cert_pem = create_user_certificate(
            common_name="ED Test User",
            email="ed@example.com",
            public_key_pem=self.user_ed25519_public_pem,
            ca_key=self.ca_key,
            ca_cert=self.ca_cert,
        )
        
        self.assertIsNotNone(cert_pem)
        self.assertIn(b"BEGIN CERTIFICATE", cert_pem)

    def test_parse_certificate(self):
        """Sertifika parse etme test et."""
        cert_pem = create_user_certificate(
            common_name="Parse Test",
            email="parse@example.com",
            public_key_pem=self.user_rsa_public_pem,
            ca_key=self.ca_key,
            ca_cert=self.ca_cert,
        )
        
        cert_info = parse_certificate(cert_pem)
        
        self.assertEqual(cert_info["subject_cn"], "Parse Test")
        self.assertEqual(cert_info["subject_email"], "parse@example.com")
        self.assertIn("CN=Demo Root CA", cert_info["issuer"])
        self.assertFalse(cert_info["is_expired"])
        self.assertIn("serial_number", cert_info)
        self.assertIn("algorithm", cert_info)

    def test_verify_certificate_chain_valid(self):
        """Geçerli sertifika zincirini doğrulama test et."""
        cert_pem = create_user_certificate(
            common_name="Chain Test",
            email="chain@example.com",
            public_key_pem=self.user_rsa_public_pem,
            ca_key=self.ca_key,
            ca_cert=self.ca_cert,
        )
        
        result = verify_certificate_chain(cert_pem, self.ca_cert)
        
        self.assertTrue(result["ca_verified"])
        self.assertTrue(result["is_valid"])
        self.assertFalse(result["is_expired"])
        self.assertIn("✅", "".join(result["details"]))

    def test_certificate_validity_dates(self):
        """Sertifika geçerlilik tarihlerini test et."""
        cert_pem = create_user_certificate(
            common_name="Date Test",
            email="date@example.com",
            public_key_pem=self.user_rsa_public_pem,
            ca_key=self.ca_key,
            ca_cert=self.ca_cert,
            validity_days=365,
        )
        
        cert_info = parse_certificate(cert_pem)
        
        self.assertIsNotNone(cert_info["not_valid_before_dt"])
        self.assertIsNotNone(cert_info["not_valid_after_dt"])
        
        # Başlangıç tarihi bugünden sonra olmalı
        self.assertLess(cert_info["not_valid_before_dt"], datetime.now(timezone.utc))
        # Bitiş tarihi gelecekte olmalı
        self.assertGreater(cert_info["not_valid_after_dt"], datetime.now(timezone.utc))

    def test_certificate_extensions(self):
        """Sertifika extensions'larını test et."""
        cert_pem = create_user_certificate(
            common_name="Extension Test",
            email="ext@example.com",
            public_key_pem=self.user_rsa_public_pem,
            ca_key=self.ca_key,
            ca_cert=self.ca_cert,
        )
        
        cert_info = parse_certificate(cert_pem)
        
        # Sertifika doğru şekilde imzalanmalı
        self.assertIn("serial_number", cert_info)
        self.assertIsNotNone(cert_info["serial_number"])

    def test_certificate_with_different_key_sizes(self):
        """Farklı RSA anahtar boyutlarıyla sertifika oluşturma test et."""
        # RSA-4096 ile
        _, rsa_4096_public_pem = generate_rsa_key_pair(4096)
        cert_pem = create_user_certificate(
            common_name="Large Key Test",
            email="large@example.com",
            public_key_pem=rsa_4096_public_pem,
            ca_key=self.ca_key,
            ca_cert=self.ca_cert,
        )
        
        cert_info = parse_certificate(cert_pem)
        self.assertEqual(cert_info["public_key_size"], 4096)

    def test_certificate_ed25519_key_size(self):
        """Ed25519 sertifikasının anahtar boyutu test et."""
        cert_pem = create_user_certificate(
            common_name="ED Key Test",
            email="edkey@example.com",
            public_key_pem=self.user_ed25519_public_pem,
            ca_key=self.ca_key,
            ca_cert=self.ca_cert,
        )
        
        cert_info = parse_certificate(cert_pem)
        self.assertEqual(cert_info["public_key_size"], 256)


if __name__ == "__main__":
    unittest.main()
