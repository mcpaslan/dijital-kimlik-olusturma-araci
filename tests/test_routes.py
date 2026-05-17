"""Routes (Integration) testleri."""

import unittest
import tempfile
import os
from app import create_app
from models.database import db, User, Certificate


class TestRoutes(unittest.TestCase):
    """Flask routes integration testleri."""

    @classmethod
    def setUpClass(cls):
        """Test öncesi setup."""
        # Geçici veritabanı kullan
        cls.db_fd, cls.db_path = tempfile.mkstemp()

    def setUp(self):
        """Her test öncesi çalışır."""
        self.app = create_app(test=True, db_path=f"sqlite:///{self.db_path}")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Her test sonrası çalışır."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @classmethod
    def tearDownClass(cls):
        """Test sonrası cleanup."""
        os.close(cls.db_fd)
        os.unlink(cls.db_path)

    def test_index_page(self):
        """Index sayfası açılma test et."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_generate_keys_page(self):
        """Anahtar oluşturma sayfası test et."""
        response = self.client.get("/keys/generate")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Anahtar", response.data)

    def test_generate_rsa_keys_post(self):
        """RSA anahtarları POST ile oluşturma test et."""
        response = self.client.post(
            "/keys/generate",
            data={
                "common_name": "Test User",
                "email": "test@example.com",
                "key_algorithm": "RSA",
                "key_size": "2048",
            },
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BEGIN PRIVATE KEY", response.data)
        self.assertIn(b"BEGIN PUBLIC KEY", response.data)
        
        # Veritabanında user oluşturulmuş mu kontrol et
        user = User.query.filter_by(email="test@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.common_name, "Test User")
        self.assertEqual(user.key_algorithm, "RSA")
        self.assertEqual(user.key_size, 2048)

    def test_generate_ed25519_keys_post(self):
        """Ed25519 anahtarları POST ile oluşturma test et."""
        response = self.client.post(
            "/keys/generate",
            data={
                "common_name": "ED User",
                "email": "ed@example.com",
                "key_algorithm": "Ed25519",
                "key_size": "256",
            },
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BEGIN PRIVATE KEY", response.data)
        
        # Veritabanında user oluşturulmuş mu kontrol et
        user = User.query.filter_by(email="ed@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.key_algorithm, "Ed25519")

    def test_list_keys_page(self):
        """Anahtar listesi sayfası test et."""
        # Önce bir user oluştur
        self.client.post(
            "/keys/generate",
            data={
                "common_name": "List Test",
                "email": "list@example.com",
                "key_algorithm": "RSA",
                "key_size": "2048",
            },
        )
        
        response = self.client.get("/keys/list")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"List Test", response.data)

    def test_certificate_creation_page(self):
        """Sertifika oluşturma sayfası test et."""
        response = self.client.get("/certificate/create")
        self.assertEqual(response.status_code, 200)

    def test_verify_page(self):
        """İmza doğrulama sayfası test et."""
        response = self.client.get("/verify/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Doğrula", response.data)

    def test_sign_page(self):
        """İmzalama sayfası test et."""
        response = self.client.get("/sign/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"İmzala", response.data)


if __name__ == "__main__":
    unittest.main()
