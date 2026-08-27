"""Construye social.db y genera el dump filtrado que se entrega a los jugadores.

Uso:  uv run seed.py
Regenera todo desde cero a partir de content.py, de modo que la base de datos
de la plataforma y el dump siempre comparten los mismos hashes.
"""
import csv
import hashlib
import random
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path

from content import USERS
from messages import CONVERSACIONES

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "social.db"
HANDOUT_DIR = BASE_DIR / "handout"
PRIVATE_DIR = BASE_DIR / "private"
SCHEMA_PATH = BASE_DIR / "schema.sql"
MICHI_DIR = BASE_DIR / "assets" / "michi"
VIAJE_DIR = BASE_DIR / "assets" / "viaje"

# Etapa 2. Ningun adjunto contiene la flag: la flag vive FUERA del repo, en una
# resena real de Google Reviews del local que aparece en la foto del viaje.
#
#   - ADJUNTO_VIAJE    zip sin cifrar con la foto del bar. Es el camino correcto.
#   - ADJUNTO_SENUELO  zip cifrado con solo fotos del gato. Callejon sin salida.
ADJUNTO_VIAJE = "viaje.zip"
ADJUNTO_SENUELO = "fotos_michi.zip"
SENUELO_PASSWORD = "michi-la-reina"


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validar(users):
    """Chequeos que evitan romper el desafio en silencio."""
    usernames = [u["username"] for u in users]
    passwords = [u["password"] for u in users]
    assert len(set(usernames)) == len(usernames), "hay usernames repetidos"
    assert len(set(passwords)) == len(passwords), "hay contrasenas repetidas"

    objetivo = [u for u in users if u["username"] == "jaimito_ar"]
    assert len(objetivo) == 1, "debe existir exactamente un jaimito_ar"
    assert objetivo[0]["password"] == "Michi2003", "la contrasena objetivo cambio"

    for u in users:
        faltan = {"username", "display_name", "email", "password", "facts", "posts"} - set(u)
        assert not faltan, f"{u.get('username')} no tiene los campos {faltan}"

    # Los mensajes solo pueden referirse a usuarios que existen.
    validos = set(usernames)
    duenos = set(CONVERSACIONES)
    assert duenos <= validos, f"buzones de usuarios inexistentes: {duenos - validos}"
    pares = {t["peer"] for hilos in CONVERSACIONES.values() for t in hilos}
    assert pares <= validos, f"interlocutores inexistentes: {pares - validos}"

    todos = [
        (dueno, m)
        for dueno, hilos in CONVERSACIONES.items()
        for t in hilos
        for m in t["mensajes"]
    ]
    for dueno, (direccion, _, _, _) in todos:
        assert direccion in ("in", "out"), f"direccion invalida en {dueno}"

    # La clave del senuelo tiene que estar exactamente una vez y en el buzon correcto.
    con_clave = [dueno for dueno, m in todos if SENUELO_PASSWORD in m[1]]
    assert con_clave == ["jaimito_ar"], (
        f"la clave del senuelo deberia aparecer una vez en el buzon de jaimito_ar, "
        f"aparece en {con_clave}"
    )
    adjuntos = sorted((dueno, m[3]) for dueno, m in todos if m[3])
    esperados = sorted(
        [("jaimito_ar", ADJUNTO_VIAJE), ("jaimito_ar", ADJUNTO_SENUELO)]
    )
    assert adjuntos == esperados, (
        f"se esperaban exactamente {esperados} en el buzon de jaimito_ar, "
        f"hay {adjuntos}"
    )
    # La contrasena de la etapa 1 no puede filtrarse en los mensajes.
    assert not any(objetivo[0]["password"] in m[1] for _, m in todos), (
        "un mensaje privado revela la contrasena de la etapa 1"
    )


def construir_db(users):
    if DB_PATH.exists():
        DB_PATH.unlink()
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    for uid, u in enumerate(users, start=1):
        db.execute(
            "INSERT INTO users (id, username, display_name, email, bio, location, "
            "joined, verified, avatar_hue, password_sha256) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                uid,
                u["username"],
                u["display_name"],
                u["email"],
                u.get("bio", ""),
                u.get("location", ""),
                u.get("joined", ""),
                int(u.get("verified", 0)),
                int(u.get("avatar_hue", 200)),
                sha256(u["password"]),
            ),
        )
        for orden, (label, value) in enumerate(u["facts"]):
            db.execute(
                "INSERT INTO facts (user_id, label, value, ord) VALUES (?,?,?,?)",
                (uid, label, value, orden),
            )
        for content, created_at, likes in u["posts"]:
            db.execute(
                "INSERT INTO posts (user_id, content, created_at, likes) VALUES (?,?,?,?)",
                (uid, content, created_at, int(likes)),
            )

    # Mensajes privados. Se insertan al final, cuando todos los ids existen.
    ids = {u["username"]: i for i, u in enumerate(users, start=1)}
    hilo_id = 0
    for dueno, hilos in CONVERSACIONES.items():
        for orden_hilo, hilo in enumerate(hilos):
            hilo_id += 1
            db.execute(
                "INSERT INTO threads (id, owner_id, peer_id, ord) VALUES (?,?,?,?)",
                (hilo_id, ids[dueno], ids[hilo["peer"]], orden_hilo),
            )
            for orden_msg, (direccion, cuerpo, cuando, adjunto) in enumerate(
                hilo["mensajes"]
            ):
                db.execute(
                    "INSERT INTO messages (thread_id, direction, body, created_at, "
                    "attachment, ord) VALUES (?,?,?,?,?,?)",
                    (hilo_id, direccion, cuerpo, cuando, adjunto, orden_msg),
                )

    db.commit()
    db.close()


def construir_dump(users):
    """CSV y SQL con id, email, usuario y hash: lo unico que ven los jugadores."""
    HANDOUT_DIR.mkdir(exist_ok=True)
    filas = [
        {
            "id": uid,
            "email": u["email"],
            "username": u["username"],
            "password_hash": sha256(u["password"]),
        }
        for uid, u in enumerate(users, start=1)
    ]
    # Se barajan para que el objetivo no quede en una posicion delatora.
    random.Random(1337).shuffle(filas)

    csv_path = HANDOUT_DIR / "facebuk_users_dump.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "email", "username", "password_hash"])
        writer.writeheader()
        writer.writerows(filas)

    sql_path = HANDOUT_DIR / "facebuk_users_dump.sql"
    lineas = [
        "-- facebuk.cl user table dump",
        "-- generated by mysqldump 10.13  Distrib 5.7.38",
        "",
        "CREATE TABLE `users` (",
        "  `id` int(11) NOT NULL AUTO_INCREMENT,",
        "  `email` varchar(255) NOT NULL,",
        "  `username` varchar(64) NOT NULL,",
        "  `password_hash` char(64) NOT NULL,",
        "  PRIMARY KEY (`id`)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;",
        "",
        "LOCK TABLES `users` WRITE;",
    ]
    for f in filas:
        email = f["email"].replace("'", "''")
        lineas.append(
            "INSERT INTO `users` VALUES ({id},'{email}','{username}','{hash}');".format(
                id=f["id"], email=email, username=f["username"], hash=f["password_hash"]
            )
        )
    lineas += ["UNLOCK TABLES;", ""]
    sql_path.write_text("\n".join(lineas), encoding="utf-8")

    return csv_path, sql_path


def _zip(destino, archivos, password=None):
    """Empaqueta `archivos` en `destino`, opcionalmente cifrado."""
    if destino.exists():
        destino.unlink()
    cmd = ["zip", "-q", "-j"]
    if password:
        cmd += ["-P", password]
    subprocess.run(cmd + [str(destino)] + [str(a) for a in archivos], check=True)
    return destino


# Ojo con la extension: .jpeg es tan valida como .jpg y antes se quedaba fuera.
EXT_IMAGEN = {".jpg", ".jpeg", ".png"}


def _imagenes(directorio):
    """Todas las imagenes de `directorio`, sin importar mayusculas ni extension."""
    return sorted(
        p for p in directorio.iterdir() if p.suffix.lower() in EXT_IMAGEN
    )


def construir_adjuntos():
    """Crea los dos adjuntos del buzon de Jaimito.

    Ninguno lleva la flag. La foto del viaje (sin cifrar) muestra el local donde hay que
    buscar la resena; el senuelo (cifrado) solo tiene fotos del gato.

    Se usa el `zip` del sistema porque zipfile no sabe escribir archivos
    cifrados. El cifrado clasico de ZIP es debil, pero cualquier gestor de
    archivos (Finder, Explorador, 7-Zip) lo abre sin instalar nada.
    """
    if shutil.which("zip") is None:
        raise SystemExit("falta el comando 'zip' (Info-ZIP), necesario para los adjuntos")

    PRIVATE_DIR.mkdir(exist_ok=True)

    # Camino correcto: las fotos del viaje, sin clave.
    fotos_viaje = _imagenes(VIAJE_DIR)
    assert fotos_viaje, f"faltan las fotos del viaje en {VIAJE_DIR}"
    viaje = _zip(PRIVATE_DIR / ADJUNTO_VIAJE, fotos_viaje)

    # Senuelo: fotos del gato y nada mas.
    fotos = _imagenes(MICHI_DIR)
    assert fotos, f"faltan las fotos de Michi en {MICHI_DIR}"
    senuelo = _zip(PRIVATE_DIR / ADJUNTO_SENUELO, fotos, SENUELO_PASSWORD)

    # La foto tiene que abrirse sin clave...
    listado = subprocess.run(
        ["unzip", "-l", str(viaje)], capture_output=True, text=True, check=True
    )
    faltan = [f.name for f in fotos_viaje if f.name not in listado.stdout]
    assert not faltan, f"al zip del viaje le faltan: {', '.join(faltan)}"

    # ...y el senuelo NO.
    sin_clave = subprocess.run(
        ["unzip", "-t", "-P", "clave-incorrecta", str(senuelo)],
        capture_output=True, text=True,
    )
    assert sin_clave.returncode != 0, "el senuelo se abre con una clave incorrecta"

    con_clave = subprocess.run(
        ["unzip", "-t", "-P", SENUELO_PASSWORD, str(senuelo)],
        capture_output=True, text=True,
    )
    assert con_clave.returncode == 0, "el senuelo no se abre con su propia clave"

    return viaje, senuelo


def main():
    validar(USERS)
    construir_db(USERS)
    csv_path, sql_path = construir_dump(USERS)
    viaje, senuelo = construir_adjuntos()
    n_msgs = sum(
        len(t["mensajes"]) for hilos in CONVERSACIONES.values() for t in hilos
    )
    print(f"OK  {len(USERS)} usuarios, {n_msgs} mensajes privados")
    print(f"    base de datos -> {DB_PATH.name}")
    print(f"    dump          -> {csv_path.relative_to(BASE_DIR)}")
    print(f"                     {sql_path.relative_to(BASE_DIR)}")
    print(f"    viaje         -> {viaje.relative_to(BASE_DIR)}  (sin clave)")
    print(f"    senuelo       -> {senuelo.relative_to(BASE_DIR)}  (clave: {SENUELO_PASSWORD})")
    print("    la flag NO se genera aca: va en la resena de Google Reviews")


if __name__ == "__main__":
    main()
