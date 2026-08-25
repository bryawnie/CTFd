import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path
from threading import Lock

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
FLAG = os.environ["LONCHERA_FLAG"]
MAX_QUANTITY = 100
ITEMS_FILE = Path(__file__).with_name("items.json")
ITEMS = json.loads(ITEMS_FILE.read_text(encoding="utf-8"))
ITEMS_BY_ID = {item["id"]: item for item in ITEMS}
USERS = {}
USERS_LOCK = Lock()


def get_user():
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    with USERS_LOCK:
        for user in USERS.values():
            if not user["revoked"] and hmac.compare_digest(user["token"], token):
                return user
    return None


@app.get("/")
def login_page():
    return render_template("login.html")


@app.get("/shop")
def shop():
    return render_template("shop.html")


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    if len(username) < 3 or len(password) < 4:
        return jsonify(error="Usuario o contraseña inválidos."), 400

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with USERS_LOCK:
        user = USERS.get(username)
        if user is None:
            user = {
                "password": password_hash,
                "credits": 1000,
                "token": secrets.token_urlsafe(32),
                "stock": {item["id"]: item["stock"] for item in ITEMS},
                "revoked": False,
            }
            USERS[username] = user
        elif not hmac.compare_digest(user["password"], password_hash):
            return jsonify(error="Usuario o contraseña inválidos."), 401
        else:
            user["token"] = secrets.token_urlsafe(32)
            user["revoked"] = False
    return jsonify(token=user["token"], credits=user["credits"])


@app.post("/api/logout")
def logout():
    user = get_user()
    if user is None:
        return jsonify(error="Autenticación requerida."), 401
    user["revoked"] = True
    return jsonify(message="Sesión cerrada.")


@app.get("/api/items")
def items():
    user = get_user()
    if user is None:
        return jsonify(error="Autenticación requerida."), 401
    catalog = [
        {**item, "stock": user["stock"][item["id"]]}
        for item in ITEMS
    ]
    return jsonify(credits=user["credits"], items=catalog)


@app.post("/api/checkout")
def checkout():
    user = get_user()
    if user is None:
        return jsonify(error="Autenticación requerida."), 401

    data = request.get_json(silent=True) or {}
    requested_items = data.get("items")
    if not isinstance(requested_items, dict) or not requested_items:
        return jsonify(error="El pedido está vacío."), 400

    total = 0
    normalized = {}
    for item_id, quantity in requested_items.items():
        item = ITEMS_BY_ID.get(item_id)
        if (
            item is None
            or not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity > MAX_QUANTITY
        ):
            return jsonify(error="Pedido inválido."), 400
        normalized[item_id] = quantity
        total += item["price"] * quantity

    if total > user["credits"]:
        return jsonify(error="No tienes suficientes créditos."), 400

    for item_id, quantity in normalized.items():
        stock = user["stock"][item_id]
        if stock is not None and quantity > stock:
            return jsonify(error="El producto está agotado."), 400

    for item_id, quantity in normalized.items():
        if user["stock"][item_id] is not None and quantity > 0:
            user["stock"][item_id] -= quantity

    user["credits"] -= total
    if normalized.get("flag", 0) > 0:
        return jsonify(credits=user["credits"], message=f"Pedido pagado. Tu premio es: {FLAG}")
    return jsonify(credits=user["credits"], message="Pedido pagado. ¡Que lo disfrutes!")


