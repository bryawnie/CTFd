import csv
import hashlib
import hmac
from pathlib import Path

from flask import Flask, render_template_string, request

app = Flask(__name__)
USERS_FILE = Path(__file__).with_name("users.csv")
FLAG = "fukers{pls_d0_n0t_us3_th1s_passw0rd}"

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Secure Login</title>
    <style>
        :root {
            color-scheme: light;
            --ink: #17202a;
            --muted: #66717d;
            --paper: #f7f4ee;
            --panel: rgba(255, 255, 255, 0.88);
            --line: #d9d8d2;
            --accent: #d85d43;
            --accent-dark: #a93d2c;
            --success: #176b4d;
        }

        * { box-sizing: border-box; }

        body {
            min-height: 100vh;
            margin: 0;
            color: var(--ink);
            background:
                radial-gradient(circle at 12% 18%, rgba(216, 93, 67, 0.14), transparent 28%),
                radial-gradient(circle at 88% 82%, rgba(38, 104, 92, 0.12), transparent 30%),
                var(--paper);
            font-family: Georgia, "Times New Roman", serif;
        }

        .shell {
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(320px, 430px);
            gap: clamp(2rem, 8vw, 8rem);
            align-items: center;
            width: min(1080px, calc(100% - 3rem));
            min-height: 100vh;
            margin: 0 auto;
            padding: 4rem 0;
        }

        .intro { max-width: 520px; }

        .eyebrow {
            margin: 0 0 1.25rem;
            color: var(--accent-dark);
            font: 700 0.75rem/1.2 Arial, sans-serif;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        h1 {
            max-width: 480px;
            margin: 0;
            font-size: clamp(3rem, 7vw, 5.8rem);
            font-weight: 400;
            line-height: 0.94;
            letter-spacing: 0;
        }

        .intro p {
            max-width: 390px;
            margin: 2rem 0 0;
            color: var(--muted);
            font: 1rem/1.65 Arial, sans-serif;
        }

        .login-panel {
            padding: clamp(1.75rem, 5vw, 3rem);
            border: 1px solid rgba(23, 32, 42, 0.1);
            border-radius: 8px;
            background: var(--panel);
            box-shadow: 0 24px 70px rgba(23, 32, 42, 0.1);
            backdrop-filter: blur(12px);
        }

        .panel-heading { margin-bottom: 2rem; }

        .panel-heading h2 {
            margin: 0 0 0.5rem;
            font-size: 1.7rem;
            font-weight: 400;
        }

        .panel-heading p {
            margin: 0;
            color: var(--muted);
            font: 0.9rem/1.5 Arial, sans-serif;
        }

        form { display: grid; gap: 1.2rem; }

        label {
            display: grid;
            gap: 0.5rem;
            color: var(--muted);
            font: 700 0.72rem/1.2 Arial, sans-serif;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        input {
            width: 100%;
            padding: 0.85rem 0.9rem;
            border: 1px solid var(--line);
            border-radius: 4px;
            color: var(--ink);
            background: #fff;
            font: 1rem Arial, sans-serif;
            outline: none;
            transition: border-color 160ms ease, box-shadow 160ms ease;
        }

        input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(216, 93, 67, 0.16);
        }

        button {
            margin-top: 0.35rem;
            padding: 0.95rem 1rem;
            border: 0;
            border-radius: 4px;
            color: #fff;
            background: var(--accent);
            font: 700 0.78rem Arial, sans-serif;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            cursor: pointer;
            transition: background 160ms ease, transform 160ms ease;
        }

        button:hover { background: var(--accent-dark); transform: translateY(-1px); }

        .message {
            margin: 1.25rem 0 0;
            color: var(--success);
            font: 0.9rem/1.5 Arial, sans-serif;
            overflow-wrap: anywhere;
        }

        @media (max-width: 720px) {
            .shell {
                grid-template-columns: 1fr;
                gap: 2.5rem;
                width: min(100% - 2rem, 500px);
                padding: 3rem 0;
            }

            h1 { font-size: clamp(3rem, 18vw, 5rem); }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="intro">
            <p class="eyebrow">Restricted access</p>
            <h1>Private area.</h1>
            <p>A quiet corner for authorized users. Enter your credentials to continue.</p>
        </section>
        <section class="login-panel">
            <header class="panel-heading">
                <h2>Sign in</h2>
                <p>Use your assigned account details.</p>
            </header>
    <form method="post">
      <label>Username <input name="username" autocomplete="username" required></label>
      <label>Password <input name="password" type="password" autocomplete="current-password" required></label>
      <button type="submit">Log in</button>
    </form>
        {% if message %}<p class="message">{{ message }}</p>{% endif %}
        </section>
  </main>
</body>
</html>"""

SECRET_PAGE = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Index of /s3cr3t</title>
</head>
<body>
    <h1>Index of /s3cr3t</h1>
    <ul>
        <li><a href="/s3cr3t/users.csv">users.csv</a></li>
    </ul>
</body>
</html>"""


def find_user(username, password):
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    with USERS_FILE.open(newline="") as users_file:
        for user in csv.DictReader(users_file):
            if user["username"].strip() == username.strip() and hmac.compare_digest(
                user["password_hash"].strip(), password_hash
            ):
                return True
    return False


@app.get("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /s3cr3t\n", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.get("/s3cr3t/users.csv")
def users_csv():
    return USERS_FILE.read_text(encoding="utf-8"), 200, {"Content-Type": "text/csv; charset=utf-8"}


@app.get("/s3cr3t")
def secret_directory():
    return SECRET_PAGE


@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    if request.method == "POST":
        if find_user(request.form.get("username", ""), request.form.get("password", "")):
            message = FLAG
        else:
            message = "Invalid credentials."
    return render_template_string(PAGE, message=message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
