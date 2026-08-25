import hashlib
import hmac
import os
import secrets
from threading import Lock

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
FLAG = os.environ["PORTAL_PAGOS_FLAG"]

COMPANIES = {
    "761234560": {
        "name": "Empresa de los Ferrocarriles del Estado",
        "email": "contacto@efe.cl",
    },
    "969892308": {
        "name": "Normangood",
        "email": "finanzas@normangood.cl",
    },
}

CODE_BY_RUT = {}
SESSIONS = set()
STATE_LOCK = Lock()


def normalize_rut(value):
    return "".join(character for character in str(value).upper() if character.isalnum())


def company_for(rut):
    normalized = normalize_rut(rut)
    company = COMPANIES.get(normalized)
    if company:
        return normalized, company

    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return normalized, {
        "name": "Empresa registrada",
        "email": f"contacto@empresa-{digest[:6]}.cl",
    }


def masked_email(email):
    local, domain = email.split("@", 1)
    visible = local[-2:] if len(local) > 2 else local
    return f"{'*' * max(5, len(local) - len(visible))}{visible}@{domain}"


def code_for(rut):
    with STATE_LOCK:
        if rut not in CODE_BY_RUT:
            CODE_BY_RUT[rut] = f"{secrets.randbelow(10000):04d}"
        return CODE_BY_RUT[rut]


def valid_session():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    with STATE_LOCK:
        return token in SESSIONS


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/access")
def access():
    data = request.get_json(silent=True) or {}
    rut, company = company_for(data.get("rut", ""))
    if not rut:
        return jsonify(error="Ingresa un RUT válido."), 400

    code_for(rut)
    return jsonify(
        rut=rut,
        company=company["name"],
        email=masked_email(company["email"]),
    )


@app.post("/api/verify")
def verify():
    data = request.get_json(silent=True) or {}
    rut, _ = company_for(data.get("rut", ""))
    code = str(data.get("code", ""))

    # Intentionally no attempt counter: the frontend lock is not a security control.
    if not rut or not hmac.compare_digest(code_for(rut), code):
        return jsonify(error="El código ingresado no es correcto."), 401

    token = secrets.token_urlsafe(32)
    with STATE_LOCK:
        SESSIONS.add(token)
    return jsonify(token=token)


@app.get("/api/invoices")
def invoices():
    if not valid_session():
        return jsonify(error="Autenticación requerida."), 401
    return jsonify(
        invoices=[
            {"id": 1, "number": "F-2026-00418",
                "date": "12/08/2026", "amount": "$1.248.900"},
            {"id": 2, "number": "F-2026-00431",
                "date": "19/08/2026", "amount": "$3.904.250"},
            {"id": 3, "number": "F-2026-00446",
                "date": "24/08/2026", "amount": "$780.600"},
        ]
    )


@app.get("/api/invoices/<int:invoice_id>")
def invoice_detail(invoice_id):
    if not valid_session():
        return jsonify(error="Autenticación requerida."), 401
    if invoice_id != 2:
        return jsonify(message="Detalle de factura disponible.")
    return jsonify(message=f"Factura con premio! {FLAG}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
