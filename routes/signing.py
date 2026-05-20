"""
Signing Routes — Metin ve dosya imzalama endpoint'leri.
"""

import os
from flask import Blueprint, render_template, request, flash, Response, current_app
from modules.signer import sign_text, sign_file, create_sig_file_content
from modules.key_manager import load_private_key_from_pem

signing_bp = Blueprint("signing", __name__, url_prefix="/sign")


@signing_bp.route("/", methods=["GET", "POST"])
def sign():
    """Metin ve dosya imzalama sayfası."""
    result = None

    if request.method == "POST":
        sign_type = request.form.get("sign_type", "text")

        # Private key PEM dosyasını al
        private_key_file = request.files.get("private_key_file")
        if not private_key_file or not private_key_file.filename:
            flash("Lütfen private key PEM dosyanızı yükleyin.", "error")
            return render_template("sign.html")

        try:
            private_key_pem = private_key_file.read()
            if not private_key_pem.strip():
                flash("Yüklenen private key dosyası boş.", "error")
                return render_template("sign.html")
            private_key = load_private_key_from_pem(private_key_pem)
        except ValueError:
            flash("Geçersiz veya bozuk PEM dosyası yüklendi. Lütfen geçerli bir private key dosyası seçin.", "error")
            return render_template("sign.html")
        except Exception as e:
            flash("Private key yüklenemedi. Lütfen dosya formatını kontrol edin.", "error")
            return render_template("sign.html")

        try:
            if sign_type == "text":
                # Metin imzalama
                text = request.form.get("text_input", "").strip()
                if not text:
                    flash("İmzalanacak metin giriniz.", "error")
                    return render_template("sign.html")

                result = sign_text(text, private_key)
                result["type"] = "text"
                result["original_data"] = text
                result["filename"] = "metin_imzasi.txt"
                result["sig_content"] = create_sig_file_content(result, "metin_imzasi.txt")

            elif sign_type == "file":
                # Dosya imzalama
                file = request.files.get("file_input")
                if not file or not file.filename:
                    flash("İmzalanacak dosyayı seçiniz.", "error")
                    return render_template("sign.html")

                file_data = file.read()
                if not file_data:
                    flash("Boş dosya imzalanamaz. Lütfen geçerli bir dosya yükleyin.", "error")
                    return render_template("sign.html")
                
                result = sign_file(file_data, private_key)
                result["type"] = "file"
                result["filename"] = file.filename
                result["sig_content"] = create_sig_file_content(result, file.filename)

        except Exception as e:
            flash(f"İmzalama hatası: {str(e)}", "error")

    return render_template("sign.html", result=result)


@signing_bp.route("/download-sig", methods=["POST"])
def download_sig():
    """İmza dosyasını (.sig) indirir."""
    sig_content = request.form.get("sig_content", "")
    filename = request.form.get("filename", "imza")

    if not sig_content:
        flash("İndirilecek imza bulunamadı.", "error")
        return render_template("sign.html")

    sig_filename = f"{os.path.splitext(filename)[0]}.sig"

    return Response(
        sig_content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={sig_filename}"},
    )
