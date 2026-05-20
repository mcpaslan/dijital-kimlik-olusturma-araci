"""Routes (Integration) testleri."""

import unittest
import tempfile
import os
import sys
from app import create_app
from models.database import db, User, Certificate


class TestRoutes(unittest.TestCase):
    """Flask routes integration testleri."""

    @classmethod
    def setUpClass(cls):
        """Test oncesi setup."""
        # Gecici dizin kullan (Windows PermissionError'u onlemek icin)
        cls.tmp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.tmp_dir, "test.db")

    def setUp(self):
        """Her test oncesi calisir."""
        self.app = create_app(test=True, db_path=f"sqlite:///{self.db_path}")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Her test sonrasi calisir."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @classmethod
    def tearDownClass(cls):
        """Test sonrasi cleanup."""
        import shutil
        try:
            shutil.rmtree(cls.tmp_dir, ignore_errors=True)
        except Exception:
            pass

    def test_index_page(self):
        """Index sayfasi acilma test et."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_generate_keys_page(self):
        """Anahtar olusturma sayfasi test et."""
        response = self.client.get("/keys/generate")
        self.assertEqual(response.status_code, 200)
        # HTML'de bulunmasi kesin olan ASCII icerik
        self.assertIn(b"common_name", response.data)

    def test_generate_rsa_keys_post(self):
        """RSA anahtarlari POST ile olusturma test et."""
        response = self.client.post(
            "/keys/generate",
            data={
                "common_name": "Test User",
                "email": "test@example.com",
                "key_algorithm": "RSA",
                "key_size": "2048",
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv16H4\n-----END PUBLIC KEY-----",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"BEGIN PRIVATE KEY", response.data)
        self.assertIn(b"BEGIN PUBLIC KEY", response.data)

        # Veritabaninda user olusturulmus mu kontrol et
        user = User.query.filter_by(email="test@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.common_name, "Test User")
        self.assertEqual(user.key_algorithm, "RSA")
        self.assertEqual(user.key_size, 2048)

    def test_generate_ed25519_keys_post(self):
        """Ed25519 anahtarlari POST ile olusturma test et."""
        response = self.client.post(
            "/keys/generate",
            data={
                "common_name": "ED User",
                "email": "ed@example.com",
                "key_algorithm": "Ed25519",
                "key_size": "256",
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAdV2\n-----END PUBLIC KEY-----",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"BEGIN PRIVATE KEY", response.data)
        self.assertIn(b"BEGIN PUBLIC KEY", response.data)

        user = User.query.filter_by(email="ed@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.key_algorithm, "Ed25519")

    def test_list_keys_page(self):
        """Anahtar listesi sayfasi test et."""
        self.client.post(
            "/keys/generate",
            data={
                "common_name": "List Test",
                "email": "list@example.com",
                "key_algorithm": "RSA",
                "key_size": "2048",
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv16H4\n-----END PUBLIC KEY-----",
            },
        )

        response = self.client.get("/keys/list")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"List Test", response.data)

    def test_certificate_creation_page(self):
        """Sertifika olusturma sayfasi test et."""
        response = self.client.get("/certificate/create")
        self.assertEqual(response.status_code, 200)

    def test_verify_page(self):
        """Imza dogrulama sayfasi test et."""
        response = self.client.get("/verify/")
        self.assertEqual(response.status_code, 200)
        # UTF-8 encoded Turkish text veya ASCII class adi ara
        self.assertIn(b"pubkey_file", response.data)
        self.assertIn(b"signature_input", response.data)

    def test_sign_page(self):
        """Imzalama sayfasi test et."""
        response = self.client.get("/sign/")
        self.assertEqual(response.status_code, 200)
        # Form elementlerini ASCII olarak kontrol et
        self.assertIn(b"text_input", response.data)
        self.assertIn(b"private_key_file", response.data)

    def test_download_public_key(self):
        """Public key indirme endpoint test et."""
        fake_pem = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0B\n-----END PUBLIC KEY-----"
        response = self.client.post(
            "/keys/download-public-key",
            data={
                "public_key_pem": fake_pem,
                "common_name": "Test User",
            },
        )
        self.assertEqual(response.status_code, 200)
        content_disp = response.headers.get("Content-Disposition", "")
        self.assertIn("attachment", content_disp)
        self.assertIn("public_key.pem", content_disp)

    def test_download_public_key_empty(self):
        """Bos public key indirme denemesi test et."""
        response = self.client.post(
            "/keys/download-public-key",
            data={"public_key_pem": "", "common_name": "Test"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_sign_page_missing_key(self):
        """Private key olmadan imzalama hatasi test et."""
        response = self.client.post(
            "/sign/",
            data={
                "sign_type": "text",
                "text_input": "test metni",
                # private_key_file yok
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # Hata mesaji olmali
        self.assertIn(b"text_input", response.data)


if __name__ == "__main__":
    unittest.main()
