import os
import sys

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    if os.name == "nt":
        app.run(host="0.0.0.0", port=port)
    else:
        os.execv(
            sys.executable,
            [sys.executable, "-m", "gunicorn", "--bind", f"0.0.0.0:{port}", "app:app"],
        )
