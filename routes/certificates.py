"""
Certificates Routes — Sertifika oluşturma ve görüntüleme endpoint'leri.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, current_app
from models.database import db, User, Certificate
from modules.certificate_manager import create_user_certificate, parse_certificate, verify_certificate_chain

certs_bp = Blueprint("certificates", __name__, url_prefix="/certificate")


@certs_bp.route("/create", methods=["GET", "POST"])
def create():
    """Sertifika oluşturma formu ve işlemi."""
    users = User.query.order_by(User.created_at.desc()).all()

    if request.method == "POST":
        user_id = request.form.get("user_id", type=int)

        if not user_id:
            flash("Lütfen bir kullanıcı seçin.", "error")
            return render_template("certificate.html", users=users)

        user = User.query.get(user_id)
        if not user:
            flash("Kullanıcı bulunamadı.", "error")
            return render_template("certificate.html", users=users)

        # Kullanıcının zaten sertifikası var mı kontrol et
        existing_cert = Certificate.query.filter_by(
            user_id=user_id, is_revoked=False
        ).first()
        if existing_cert:
            flash("Bu kullanıcının zaten aktif bir sertifikası var.", "warning")
            return redirect(url_for("certificates.view", cert_id=existing_cert.id))

        try:
            # CA'yı al
            ca_key = current_app.config["CA_KEY"]
            ca_cert = current_app.config["CA_CERT"]

            # Sertifika oluştur
            cert_pem = create_user_certificate(
                common_name=user.common_name,
                email=user.email,
                public_key_pem=user.public_key_pem.encode("utf-8"),
                ca_key=ca_key,
                ca_cert=ca_cert,
            )

            # Sertifika bilgilerini parse et
            cert_info = parse_certificate(cert_pem)

            # Veritabanına kaydet
            certificate = Certificate(
                user_id=user.id,
                serial_number=cert_info["serial_number"],
                certificate_pem=cert_pem.decode("utf-8"),
                issuer=cert_info["issuer"],
                valid_from=cert_info["not_valid_before_dt"],
                valid_until=cert_info["not_valid_after_dt"],
                algorithm=cert_info["algorithm"],
            )
            db.session.add(certificate)
            db.session.commit()

            flash("Sertifika başarıyla oluşturuldu!", "success")
            return redirect(url_for("certificates.view", cert_id=certificate.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Sertifika oluşturma hatası: {str(e)}", "error")

    return render_template("certificate.html", users=users)


@certs_bp.route("/view/<int:cert_id>")
def view(cert_id):
    """Sertifika detaylarını görüntüler."""
    certificate = Certificate.query.get_or_404(cert_id)
    cert_info = parse_certificate(certificate.certificate_pem.encode("utf-8"))

    # CA ile doğrulama
    ca_cert = current_app.config["CA_CERT"]
    chain_result = verify_certificate_chain(
        certificate.certificate_pem.encode("utf-8"), ca_cert
    )

    return render_template(
        "certificate_view.html",
        certificate=certificate,
        cert_info=cert_info,
        chain_result=chain_result,
    )


@certs_bp.route("/list")
def list_certs():
    """Tüm sertifikaları listeler."""
    certificates = Certificate.query.order_by(Certificate.created_at.desc()).all()
    return render_template("certificate_list.html", certificates=certificates)


@certs_bp.route("/download/<int:cert_id>")
def download(cert_id):
    """Sertifikayı PEM dosyası olarak indirir."""
    certificate = Certificate.query.get_or_404(cert_id)
    user = User.query.get(certificate.user_id)
    filename = f"{user.common_name.replace(' ', '_').lower()}_certificate.pem"

    return Response(
        certificate.certificate_pem,
        mimetype="application/x-pem-file",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
