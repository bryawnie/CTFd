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
  <title>Private area</title>
</head>
<body>
  <main>
    <h1>Private area</h1>
    <p>Sign in to continue.</p>
    <form method="post">
      <label>Username <input name="username" autocomplete="username" required></label>
      <label>Password <input name="password" type="password" autocomplete="current-password" required></label>
      <button type="submit">Log in</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
  </main>
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
