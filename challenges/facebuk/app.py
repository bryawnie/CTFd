"""FaceBuk - plataforma social ficticia para un CTF de OSINT."""
import hashlib
import os
import sqlite3
from pathlib import Path

from flask import (
    Flask, g, redirect, render_template, request, send_from_directory,
    session, url_for,
)

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "social.db"
# Los adjuntos viven fuera de static/: solo se entregan tras iniciar sesion.
PRIVATE_DIR = BASE_DIR / "private"

app = Flask(__name__)
# Solo sirve para firmar la cookie de sesion en una red local; no protege nada
# del desafio. La flag no vive en el servidor, sino dentro del zip cifrado.
app.secret_key = os.environ.get("SECRET_KEY", "facebuk-ctf-local")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def usuario_actual():
    """Fila del usuario con sesion iniciada, o None."""
    username = session.get("username")
    if not username:
        return None
    return get_db().execute(
        "SELECT id, username, display_name, avatar_hue FROM users WHERE username = ?",
        (username,),
    ).fetchone()


@app.route("/")
def index():
    db = get_db()
    destacados = db.execute(
        "SELECT username, display_name, bio, location, verified, avatar_hue "
        "FROM users ORDER BY RANDOM() LIMIT 6"
    ).fetchall()
    total = db.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
    return render_template("index.html", destacados=destacados, total=total)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/privacidad")
def privacidad():
    return render_template("privacidad.html")


@app.route("/buscar")
def buscar():
    q = request.args.get("q", "").strip()
    resultados = []
    if q:
        like = f"%{q}%"
        # Consulta parametrizada a proposito: el desafio es OSINT, no inyeccion SQL.
        resultados = get_db().execute(
            "SELECT username, display_name, bio, location, verified, avatar_hue "
            "FROM users "
            "WHERE username LIKE ? OR display_name LIKE ? OR bio LIKE ? "
            "ORDER BY display_name LIMIT 30",
            (like, like, like),
        ).fetchall()
    return render_template("buscar.html", q=q, resultados=resultados)


@app.route("/u/<username>")
def perfil(username):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user is None:
        return render_template("404.html", username=username), 404
    facts = db.execute(
        "SELECT label, value FROM facts WHERE user_id = ? ORDER BY ord, id",
        (user["id"],),
    ).fetchall()
    posts = db.execute(
        "SELECT content, created_at, likes FROM posts WHERE user_id = ? "
        "ORDER BY created_at DESC",
        (user["id"],),
    ).fetchall()
    return render_template("perfil.html", user=user, facts=facts, posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = get_db().execute(
        "SELECT username, password_sha256 FROM users WHERE username = ?", (username,)
    ).fetchone()

    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if user is None or digest != user["password_sha256"]:
        return render_template(
            "login.html", error="Usuario o contrasena incorrectos.", username=username
        ), 401

    session["username"] = user["username"]
    return redirect(url_for("mensajes"))


@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("index"))


@app.route("/mensajes")
def mensajes():
    user = usuario_actual()
    if user is None:
        return redirect(url_for("login"))

    db = get_db()
    hilos = db.execute(
        "SELECT t.id, u.username AS peer_username, u.display_name AS peer_display_name, "
        "       u.avatar_hue AS peer_hue "
        "FROM threads t JOIN users u ON u.id = t.peer_id "
        "WHERE t.owner_id = ? ORDER BY t.ord, t.id",
        (user["id"],),
    ).fetchall()

    conversaciones = []
    for hilo in hilos:
        msgs = db.execute(
            "SELECT direction, body, created_at, attachment FROM messages "
            "WHERE thread_id = ? ORDER BY ord, id",
            (hilo["id"],),
        ).fetchall()
        conversaciones.append(
            {
                "peer_username": hilo["peer_username"],
                "peer_display_name": hilo["peer_display_name"],
                "peer_hue": hilo["peer_hue"],
                "mensajes": msgs,
            }
        )
    return render_template("mensajes.html", user=user, conversaciones=conversaciones)


@app.route("/descargar/<path:filename>")
def descargar(filename):
    """Entrega un adjunto solo si pertenece a un hilo del usuario con sesion."""
    user = usuario_actual()
    if user is None:
        return redirect(url_for("login"))

    permitido = get_db().execute(
        "SELECT 1 FROM messages m JOIN threads t ON t.id = m.thread_id "
        "WHERE t.owner_id = ? AND m.attachment = ? LIMIT 1",
        (user["id"], filename),
    ).fetchone()
    if permitido is None:
        return render_template("404.html", username=None), 404

    return send_from_directory(PRIVATE_DIR, filename, as_attachment=True)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", username=None), 404


if __name__ == "__main__":
    # 5000 lo ocupa el receptor AirPlay en macOS, por eso 8000 por defecto.
    puerto = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=puerto, debug=False)
