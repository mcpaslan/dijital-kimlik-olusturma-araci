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
        signature_b64 = request.form.get("signature_b64", "").strip()
        hash_hex = request.form.get("hash_hex", "").strip()

        if not signature_b64 or not hash_hex:
            flash("İmza veya Hash verisi tarayıcıdan alınamadı.", "error")
            return render_template("sign.html")

        try:
            import base64
            from datetime import datetime, timezone
            
            # İmza boyutuna göre algoritmayı otomatik algıla
            sig_bytes = base64.b64decode(signature_b64)
            if len(sig_bytes) == 64:
                algorithm = "Ed25519"
            else:
                algorithm = "RSA-PSS + SHA-256 (Prehashed)"

            result = {
                "signature_b64": signature_b64,
                "hash_hex": hash_hex,
                "algorithm": algorithm,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            }

            if sign_type == "text":
                text = request.form.get("text_input", "").strip()
                result["type"] = "text"
                result["original_data"] = text
                result["filename"] = "metin_imzasi.txt"
                result["sig_content"] = create_sig_file_content(result, "metin_imzasi.txt")

            elif sign_type == "file":
                filename = request.form.get("filename", "dosya.dat").strip()
                result["type"] = "file"
                result["filename"] = filename
                result["sig_content"] = create_sig_file_content(result, filename)

        except Exception as e:
            flash(f"İmza işleme hatası: {str(e)}", "error")

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
