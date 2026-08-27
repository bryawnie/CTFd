-- Esquema de la plataforma "FaceBuk"
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS threads;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS facts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id           INTEGER PRIMARY KEY,
    username     TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    email        TEXT NOT NULL,
    bio          TEXT NOT NULL DEFAULT '',
    location     TEXT NOT NULL DEFAULT '',
    joined       TEXT NOT NULL DEFAULT '',
    verified     INTEGER NOT NULL DEFAULT 0,
    avatar_hue   INTEGER NOT NULL DEFAULT 0,
    -- sha256 de la contraseña: mismo valor que aparece en el dump filtrado
    password_sha256 TEXT NOT NULL
);

CREATE TABLE facts (
    id      INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    label   TEXT NOT NULL,
    value   TEXT NOT NULL,
    ord     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE posts (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    content    TEXT NOT NULL,
    created_at TEXT NOT NULL,
    likes      INTEGER NOT NULL DEFAULT 0
);

-- Mensajes privados: solo visibles tras iniciar sesion como el dueno del buzon.
CREATE TABLE threads (
    id           INTEGER PRIMARY KEY,
    owner_id     INTEGER NOT NULL REFERENCES users(id),
    peer_id      INTEGER NOT NULL REFERENCES users(id),
    ord          INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE messages (
    id         INTEGER PRIMARY KEY,
    thread_id  INTEGER NOT NULL REFERENCES threads(id),
    direction  TEXT NOT NULL CHECK (direction IN ('in','out')),
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL,
    attachment TEXT,
    ord        INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_posts_user ON posts(user_id, created_at DESC);
CREATE INDEX idx_threads_owner ON threads(owner_id, ord);
CREATE INDEX idx_messages_thread ON messages(thread_id, ord);
CREATE INDEX idx_facts_user ON facts(user_id, ord);
