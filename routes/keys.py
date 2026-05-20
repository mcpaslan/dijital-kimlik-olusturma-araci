"""
Keys Routes — Anahtar çifti oluşturma endpoint'leri.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from models.database import db, User
from modules.key_manager import generate_rsa_key_pair, generate_ed25519_key_pair

keys_bp = Blueprint("keys", __name__, url_prefix="/keys")


@keys_bp.route("/generate", methods=["GET", "POST"])
def generate():
    """Anahtar çifti oluşturma formu ve işlemi."""
    if request.method == "POST":
        common_name = request.form.get("common_name", "").strip()
        email = request.form.get("email", "").strip()
        key_algorithm = request.form.get("key_algorithm", "RSA").strip()
        key_size = int(request.form.get("key_size", 2048))

        # Doğrulama
        if not common_name or not email:
            flash("Ad Soyad ve E-posta alanları zorunludur.", "error")
            return render_template("generate_keys.html")

        if key_algorithm not in ("RSA", "Ed25519"):
            flash("Geçersiz anahtar algoritması.", "error")
            return render_template("generate_keys.html")

        if key_algorithm == "RSA" and key_size not in (2048, 4096):
            flash("RSA anahtar boyutu 2048 veya 4096 olmalıdır.", "error")
            return render_template("generate_keys.html")

        # Client-side'dan gelen Public Key'i al
        public_key_pem = request.form.get("public_key_pem", "").strip()

        if not public_key_pem:
            flash("Public Key bilgisi tarayıcıdan alınamadı.", "error")
            return render_template("generate_keys.html")

        try:
            # Kullanıcıyı veritabanına kaydet (sadece public key)
            user = User(
                common_name=common_name,
                email=email,
                public_key_pem=public_key_pem,
                key_algorithm=key_algorithm,
                key_size=key_size,
            )
            db.session.add(user)
            db.session.commit()

            return render_template(
                "generate_keys.html",
                success=True,
                user=user,
                public_key_pem=public_key_pem,
            )

        except Exception as e:
            db.session.rollback()
            flash(f"Anahtar oluşturma hatası: {str(e)}", "error")

    return render_template("generate_keys.html")


@keys_bp.route("/download-private-key", methods=["POST"])
def download_private_key():
    """Private key'i PEM dosyası olarak indirir."""
    private_key_pem = request.form.get("private_key_pem", "")
    common_name = request.form.get("common_name", "kullanici")

    if not private_key_pem:
        flash("İndirilecek private key bulunamadı.", "error")
        return redirect(url_for("keys.generate"))

    filename = f"{common_name.replace(' ', '_').lower()}_private_key.pem"

    return Response(
        private_key_pem,
        mimetype="application/x-pem-file",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@keys_bp.route("/download-public-key", methods=["POST"])
def download_public_key():
    """Public key'i PEM dosyası olarak indirir."""
    public_key_pem = request.form.get("public_key_pem", "")
    common_name = request.form.get("common_name", "kullanici")

    if not public_key_pem:
        flash("İndirilecek public key bulunamadı.", "error")
        return redirect(url_for("keys.generate"))

    filename = f"{common_name.replace(' ', '_').lower()}_public_key.pem"

    return Response(
        public_key_pem,
        mimetype="application/x-pem-file",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@keys_bp.route("/list")
def list_keys():
    """Kayıtlı kullanıcıları ve public key'lerini listeler."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("list_keys.html", users=users)
