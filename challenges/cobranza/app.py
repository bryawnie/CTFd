"""
Portal de Cobranzas "Legacy" - Reto CTF de SQL Injection
---------------------------------------------------------
Narrativa: El modulo de cobranzas fue migrado de DynamoDB (NoSQL) a SQL
(Aurora/SQLite) "a la rapida". Los inputs se concatenan directamente en las
consultas crudas, sin parametrizar => SQL Injection.

Objetivo del reto:
  1) Saltarse el login (auth bypass):  ' OR '1'='1' --
  2) Marcar la deuda de $1.000.000 como "pagada" para obtener la flag:
        '; UPDATE facturas SET estado='pagada' WHERE monto=1000000 --
"""
import os
import glob
import time
import uuid
import sqlite3
import threading
from flask import (Flask, request, redirect, url_for, session,
                   render_template_string)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())
FLAG = os.environ["COBRANZA_FLAG"]

# --- Aislamiento por jugador -------------------------------------------------
# Cada sesion (cookie firmada) tiene su PROPIA copia de la BD, para que el pago
# de un jugador no afecte a los demas. Con tope duro (LRU) y TTL de inactividad
# para no acumular archivos indefinidamente.
DB_DIR = os.environ.get("DB_DIR", "/tmp/ctf")
MAX_SESSIONS = int(os.environ.get("MAX_SESSIONS", "200"))
SESSION_TTL = int(os.environ.get("SESSION_TTL", "3600"))  # seg de inactividad

_sessions = {}                     # sid -> last_seen (epoch)
_sessions_lock = threading.Lock()

SEED_SQL = """
    CREATE TABLE empresas (
        id INTEGER PRIMARY KEY, nombre TEXT, rut TEXT,
        password TEXT, es_admin INTEGER
    );
    CREATE TABLE facturas (
        id INTEGER PRIMARY KEY, empresa TEXT, monto INTEGER, estado TEXT
    );
    INSERT INTO empresas (nombre, rut, password, es_admin) VALUES
        ('Cobranzas Internas SpA', '77.000.000-0', 'S3gur1dad#Migrac10n!2024', 1),
        ('ACME Retail Ltda',       '76.111.111-1', 'acme2023',                 0);
    INSERT INTO facturas (empresa, monto, estado) VALUES
        ('ACME Retail Ltda',    120000,  'pendiente'),
        ('ACME Retail Ltda',    45000,   'pagada'),
        ('Deudora Global SpA',  1000000, 'pendiente'),
        ('Ferreteria El Clavo', 8900,    'pendiente'),
        ('Transportes Andes',   230000,  'pagada');
"""


def _db_path(sid):
    return os.path.join(DB_DIR, sid + ".db")


def _seed_db(path):
    """Crea una BD nueva (esquema + datos semilla) en `path`."""
    conn = sqlite3.connect(path)
    conn.executescript(SEED_SQL)
    conn.commit()
    conn.close()


def _evict(sid):
    """Descarta una sesion: borra su .db y su entrada del registro."""
    _sessions.pop(sid, None)
    try:
        os.remove(_db_path(sid))
    except OSError:
        pass


def _sweep(now):
    """Purga sesiones inactivas (TTL) y aplica el tope duro (LRU)."""
    for sid, seen in list(_sessions.items()):
        if now - seen > SESSION_TTL:
            _evict(sid)
    if len(_sessions) > MAX_SESSIONS:
        sobrantes = sorted(_sessions.items(), key=lambda kv: kv[1])
        for sid, _ in sobrantes[:len(_sessions) - MAX_SESSIONS]:
            _evict(sid)


@app.before_request
def _ensure_session_db():
    """Asigna un sid por navegador y garantiza su BD aislada."""
    now = time.time()
    sid = session.get("sid")
    if not sid:
        sid = uuid.uuid4().hex
        session["sid"] = sid
    with _sessions_lock:
        _sessions[sid] = now       # marcar como la mas reciente ANTES del barrido
        _sweep(now)                # (asi la sesion actual nunca es victima del LRU)
        if not os.path.exists(_db_path(sid)):
            _seed_db(_db_path(sid))


def get_db():
    conn = sqlite3.connect(_db_path(session["sid"]))
    conn.row_factory = sqlite3.Row
    return conn


PAGE = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Finanzas - Cuentas por Cobrar</title>
<style>
  :root{
    --navy:#132a4f; --navy-2:#1c3a68; --blue:#2f6bef; --blue-soft:#dfe9ff;
    --bg:#f4f6fa; --card:#ffffff; --border:#e6eaf1; --text:#1b2b4b; --muted:#8a94a6;
    --amber:#f5a623; --amber-soft:#fdeccb; --orange:#f5772e;
    --red:#e5484d; --red-soft:#fde3e3; --green:#12a150; --green-soft:#d7f4e3;
  }
  *{box-sizing:border-box}
  body{font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;margin:0;
       background:var(--bg);color:var(--text);line-height:1.5}
  a{color:var(--blue);text-decoration:none}
  /* ---- top bar ---- */
  .topbar{background:var(--navy);color:#fff;padding:.85rem 1.5rem;display:flex;
          align-items:center;justify-content:space-between}
  .topbar .brand{font-weight:700;font-size:1.05rem;letter-spacing:.2px}
  .topbar .brand span{color:#9db9f2;font-weight:500}
  .topbar .user{font-size:.85rem;color:#c7d4ea;display:flex;gap:1rem;align-items:center}
  .wrap{max-width:1040px;margin:0 auto;padding:1.5rem}
  /* ---- login ---- */
  .login-shell{min-height:calc(100vh - 56px);display:flex;align-items:center;justify-content:center;padding:1.5rem}
  .login-card{background:var(--card);border:1px solid var(--border);border-radius:14px;
              box-shadow:0 12px 40px rgba(19,42,79,.10);width:100%;max-width:400px;overflow:hidden}
  .login-card .head{background:var(--navy);color:#fff;padding:1.1rem 1.3rem}
  .login-card .head h2{margin:0;font-size:1.1rem}
  .login-card .head p{margin:.2rem 0 0;font-size:.8rem;color:#9db9f2}
  .login-card .body{padding:1.3rem}
  label{display:block;font-size:.78rem;color:var(--muted);margin:.6rem 0 .25rem;font-weight:600;
        text-transform:uppercase;letter-spacing:.4px}
  input[type=text],input[type=password]{width:100%;padding:.6rem .7rem;border:1px solid var(--border);
        border-radius:8px;font-size:.95rem;background:#fbfcfe}
  input:focus{outline:none;border-color:var(--blue);box-shadow:0 0 0 3px var(--blue-soft)}
  button{background:var(--blue);color:#fff;border:0;padding:.6rem 1.1rem;border-radius:8px;
         cursor:pointer;font-weight:600;font-size:.9rem}
  button:hover{background:#255ad4}
  .err{color:var(--red);font-size:.85rem;margin-top:.7rem}
  /* ---- cards ---- */
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem;margin-bottom:1.4rem}
  .card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1rem 1.1rem;
        display:flex;gap:.85rem;align-items:flex-start}
  .card .ic{width:42px;height:42px;border-radius:10px;flex:0 0 42px;display:flex;align-items:center;
            justify-content:center;color:#fff;font-size:1.2rem;font-weight:700}
  .ic.blue{background:var(--blue)} .ic.amber{background:var(--amber)}
  .ic.orange{background:var(--orange)} .ic.red{background:var(--red)} .ic.green{background:var(--green)}
  .card .lbl{font-size:.8rem;color:var(--muted)}
  .card .val{font-size:1.25rem;font-weight:700;color:var(--text)}
  /* ---- panel + table ---- */
  .panel{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden}
  .panel .ph{padding:1rem 1.2rem;border-bottom:1px solid var(--border);display:flex;
             align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap}
  .panel .ph h3{margin:0;font-size:1rem}
  .search{display:flex;gap:.5rem}
  .search input{width:280px}
  table{width:100%;border-collapse:collapse}
  th{font-size:.72rem;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);
     text-align:left;padding:.7rem 1.2rem;border-bottom:1px solid var(--border)}
  td{padding:.75rem 1.2rem;border-bottom:1px solid var(--border);font-size:.92rem}
  tr:last-child td{border-bottom:0}
  .pill{display:inline-block;padding:.2rem .7rem;border-radius:999px;font-size:.78rem;font-weight:600}
  .pill.pagada{background:var(--green-soft);color:var(--green)}
  .pill.pendiente{background:var(--red-soft);color:var(--red)}
  .msg{font-size:.82rem;color:var(--muted)}
  .flag{margin:1.2rem 0 0;background:var(--green);color:#fff;padding:1rem 1.2rem;border-radius:12px;
        font-size:1.05rem;word-break:break-all;box-shadow:0 8px 24px rgba(18,161,80,.25)}
  .flag b{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
</style>
</head>
<body>
{% if not logged_in %}
  <div class="login-shell">
    <form class="login-card" method="post" action="{{ url_for('login') }}">
      <div class="head"><h2>Finanzas</h2><p>Cuentas por cobrar &middot; Acceso empresas cliente</p></div>
      <div class="body">
        <label>RUT</label>
        <input type="text" name="rut" placeholder="77.000.000-0" autocomplete="off">
        <label>Contrasena</label>
        <input type="password" name="password" placeholder="********" autocomplete="off">
        <div style="margin-top:1rem"><button type="submit">Ingresar</button></div>
        {% if error %}<p class="err">{{ error }}</p>{% endif %}
      </div>
    </form>
  </div>
{% else %}
  <div class="topbar">
    <div class="brand">Finanzas <span>&middot; Cuentas por cobrar</span></div>
    <div class="user">{{ empresa }} <a href="{{ url_for('logout') }}">Salir</a></div>
  </div>
  <div class="wrap">
    <div class="cards">
      <div class="card"><div class="ic blue">&#8595;</div>
        <div><div class="lbl">Total por cobrar</div><div class="val">${{ total_cobrar }}</div></div></div>
      <div class="card"><div class="ic red">&#33;</div>
        <div><div class="lbl">Pendiente</div><div class="val">${{ total_pendiente }}</div></div></div>
      <div class="card"><div class="ic green">&#10003;</div>
        <div><div class="lbl">Pagado</div><div class="val">${{ total_pagado }}</div></div></div>
      <div class="card"><div class="ic amber">&#9203;</div>
        <div><div class="lbl">Documentos</div><div class="val">{{ facturas|length }}</div></div></div>
    </div>

    <div class="panel">
      <div class="ph">
        <h3>Documentos</h3>
        <form class="search" method="get" action="{{ url_for('index') }}">
          <input type="text" name="q" placeholder="Buscar por cliente..." autocomplete="off">
          <button type="submit">Buscar</button>
        </form>
      </div>
      {% if msg %}<div style="padding:.5rem 1.2rem" class="msg">{{ msg }}</div>{% endif %}
      <table>
        <tr><th>#</th><th>Cliente</th><th>Monto</th><th>Estado</th></tr>
        {% for f in facturas %}
          <tr>
            <td>#{{ f['id'] }}</td>
            <td>{{ f['empresa'] }}</td>
            <td>${{ f['monto_fmt'] }}</td>
            <td><span class="pill {{ f['estado'] }}">{{ 'Pagado' if f['estado']=='pagada' else 'Vencido' }}</span></td>
          </tr>
        {% endfor %}
      </table>
    </div>

    {% if flag %}
      <div class="flag">Deuda de $1.000.000 marcada como pagada &mdash; FLAG: <b>{{ flag }}</b></div>
    {% endif %}
  </div>
{% endif %}
</body>
</html>
"""


def million_is_paid():
    conn = get_db()
    row = conn.execute("SELECT estado FROM facturas WHERE monto = 1000000").fetchone()
    conn.close()
    return row is not None and row["estado"].lower() == "pagada"




def clp(n):
    return "{:,}".format(int(n)).replace(",", ".")


def facturas_dicts(rows):
    """Convierte filas de facturas en dicts con monto formateado (CLP)."""
    result = []
    for r in rows:
        d = dict(r)
        d["monto_fmt"] = clp(d.get("monto", 0))
        result.append(d)
    return result


def render_home(display_facturas, msg=None):
    """Renderiza el dashboard. Las tarjetas-resumen y la flag se calculan
    siempre sobre la tabla completa; la tabla muestra display_facturas."""
    conn = get_db()
    full = conn.execute(
        "SELECT id, empresa, monto, estado FROM facturas ORDER BY id"
    ).fetchall()
    conn.close()
    tp = tpag = 0
    for r in full:
        if str(r["estado"]).lower() == "pagada":
            tpag += r["monto"]
        else:
            tp += r["monto"]
    return render_template_string(
        PAGE, logged_in=True, empresa=session.get("empresa", ""),
        facturas=display_facturas, flag=(FLAG if million_is_paid() else None),
        total_cobrar=clp(tp + tpag), total_pendiente=clp(tp),
        total_pagado=clp(tpag), error=None, msg=msg,
    )


@app.route("/")
def index():
    if not session.get("logged_in"):
        return render_template_string(
            PAGE, logged_in=False, empresa="", facturas=[], flag=None,
            total_cobrar="0", total_pendiente="0", total_pagado="0",
            error=request.args.get("error"), msg=request.args.get("msg"),
        )
    q = request.args.get("q")
    if q is None:
        # Sin busqueda: estado de cuenta completo.
        conn = get_db()
        rows = conn.execute(
            "SELECT id, empresa, monto, estado FROM facturas ORDER BY id"
        ).fetchall()
        conn.close()
        return render_home(facturas_dicts(rows), msg=request.args.get("msg"))

    # Busqueda por GET (patron PRG-friendly: F5 repite el GET sin reenviar
    # formulario). VULNERABLE: el input se concatena crudo y se ejecuta cada
    # sentencia (como un driver con multi-statements, ej. mysql2/pg),
    # mostrando las filas del SELECT. Esto habilita:
    #   - busqueda parcial: MULTI            -> encuentra MULTIFRUTA S.A.
    #   - dump:             ' OR 1=1 --      (el -- comenta el %' final)
    #   - stacked update:   '; UPDATE facturas SET estado='pagada' WHERE monto=1000000 --
    query = ("SELECT id, empresa, monto, estado FROM facturas "
             "WHERE empresa LIKE '%%%s%%'" % q)
    conn = get_db()
    cur = conn.cursor()
    result_rows = []
    try:
        for stmt in query.split(";"):
            if not stmt.strip():
                continue
            cur.execute(stmt)
            if cur.description is not None:  # fue un SELECT -> capturar filas
                result_rows = cur.fetchall()
        conn.commit()
    except Exception as e:
        conn.close()
        return render_home([], msg="Error SQL: %s" % e)
    conn.close()
    display = facturas_dicts(result_rows)
    if display:
        msg = "%d resultado(s) para \"%s\"." % (len(display), q)
    else:
        # Sin coincidencias: tabla vacia. La flag igual aparece si el payload
        # marco la deuda como pagada (render_home la calcula desde la BD).
        msg = "Sin coincidencias para \"%s\"." % q
    return render_home(display, msg=msg)


@app.route("/login", methods=["POST"])
def login():
    rut = request.form.get("rut", "")
    password = request.form.get("password", "")
    # VULNERABLE: input concatenado directamente en la consulta cruda.
    query = ("SELECT * FROM empresas WHERE rut = '%s' AND password = '%s'"
             % (rut, password))
    conn = get_db()
    try:
        row = conn.execute(query).fetchone()
    except Exception as e:
        conn.close()
        return redirect(url_for("index", error="Error SQL: %s" % e))
    conn.close()
    if row:
        session["logged_in"] = True
        session["empresa"] = row["nombre"]
        return redirect(url_for("index"))
    return redirect(url_for("index", error="Credenciales invalidas."))


@app.route("/logout")
def logout():
    # Cierra sesion pero conserva 'sid' -> el jugador mantiene su estado/BD.
    session.pop("logged_in", None)
    session.pop("empresa", None)
    return redirect(url_for("index"))


# Arranque: directorio limpio de BDs por sesion (estado fresco al reiniciar).
os.makedirs(DB_DIR, exist_ok=True)
for _f in glob.glob(os.path.join(DB_DIR, "*.db")):
    try:
        os.remove(_f)
    except OSError:
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
