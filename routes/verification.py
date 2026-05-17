"""
Verification Routes — İmza doğrulama endpoint'leri.
"""

from flask import Blueprint, render_template, request, flash, current_app
from cryptography import x509
from models.database import Certificate
from modules.verifier import (
    verify_text,
    verify_file,
    parse_sig_file,
    load_public_key_from_pem,
    load_public_key_from_certificate,
)
from modules.certificate_manager import parse_certificate, verify_certificate_chain

verification_bp = Blueprint("verification", __name__, url_prefix="/verify")


@verification_bp.route("/", methods=["GET", "POST"])
def verify():
    """İmza doğrulama sayfası."""
    result = None

    if request.method == "POST":
        verify_type = request.form.get("verify_type", "text")
        key_source = request.form.get("key_source", "public_key")

        # Public key veya sertifika yükle
        try:
            if key_source == "certificate":
                cert_file = request.files.get("cert_file")
                if not cert_file or not cert_file.filename:
                    flash("Lütfen sertifika dosyasını yükleyin.", "error")
                    return render_template("verify.html")

                cert_pem = cert_file.read()
                if not cert_pem.strip():
                    flash("Yüklenen sertifika dosyası boş.", "error")
                    return render_template("verify.html")
                    
                public_key = load_public_key_from_certificate(cert_pem)

                # Sertifika bilgisini parse et
                cert_info = parse_certificate(cert_pem)
                
                # Sertifika zinciri doğrulama
                ca_cert = current_app.config["CA_CERT"]
                chain_result = verify_certificate_chain(cert_pem, ca_cert)
                
                # Veritabanında revoke durumunu kontrol et
                cert = x509.load_pem_x509_certificate(cert_pem)
                serial_hex = format(cert.serial_number, "X")
                db_cert = Certificate.query.filter_by(serial_number=serial_hex).first()
                
                if db_cert and db_cert.is_revoked:
                    chain_result["is_valid"] = False
                    chain_result["details"].insert(0, f"❌ Sertifika iptal edilmiş — Sebep: {db_cert.revoke_reason}")
            else:
                pubkey_file = request.files.get("pubkey_file")
                if not pubkey_file or not pubkey_file.filename:
                    flash("Lütfen public key dosyasını yükleyin.", "error")
                    return render_template("verify.html")

                pubkey_pem = pubkey_file.read()
                if not pubkey_pem.strip():
                    flash("Yüklenen public key dosyası boş.", "error")
                    return render_template("verify.html")
                    
                public_key = load_public_key_from_pem(pubkey_pem)
                chain_result = None
                cert_info = None

        except ValueError:
            flash("Geçersiz veya bozuk PEM dosyası yüklendi. Lütfen dosya formatını kontrol edin.", "error")
            return render_template("verify.html")
        except Exception as e:
            flash("Anahtar/Sertifika işlenirken beklenmeyen bir hata oluştu.", "error")
            return render_template("verify.html")

        # İmza bilgisini al
        signature_b64 = ""
        sig_file = request.files.get("sig_file")
        if sig_file and sig_file.filename:
            sig_content = sig_file.read().decode("utf-8")
            if not sig_content.strip():
                flash("Yüklenen imza dosyası boş.", "error")
                return render_template("verify.html")
            try:
                sig_data = parse_sig_file(sig_content)
                signature_b64 = sig_data.get("signature_b64", "")
            except Exception:
                flash("İmza dosyası (.sig) formatı hatalı.", "error")
                return render_template("verify.html")
        else:
            signature_b64 = request.form.get("signature_input", "").strip()

        if not signature_b64:
            flash("Lütfen imza değerini girin veya .sig dosyası yükleyin.", "error")
            return render_template("verify.html")

        try:
            if verify_type == "text":
                # Metin doğrulama
                text = request.form.get("text_input", "").strip()
                if not text:
                    flash("Doğrulanacak metin giriniz.", "error")
                    return render_template("verify.html")

                result = verify_text(text, signature_b64, public_key)
                result["type"] = "text"

            elif verify_type == "file":
                # Dosya doğrulama
                file = request.files.get("file_input")
                if not file or not file.filename:
                    flash("Doğrulanacak dosyayı seçiniz.", "error")
                    return render_template("verify.html")

                file_data = file.read()
                if not file_data:
                    flash("Boş dosya doğrulanamaz. Lütfen geçerli bir dosya yükleyin.", "error")
                    return render_template("verify.html")
                    
                result = verify_file(file_data, signature_b64, public_key)
                result["type"] = "file"
                result["filename"] = file.filename

            # Sertifika bilgilerini sonuca ekle
            if chain_result:
                result["chain_result"] = chain_result
                result["cert_info"] = cert_info

        except Exception as e:
            flash(f"Doğrulama hatası: {str(e)}", "error")

    return render_template("verify.html", result=result)
