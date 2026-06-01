from flask import Flask, render_template, send_from_directory

from pathlib import Path

app = Flask(__name__)

DOCS_DIR = Path(__file__).resolve().parent / "docs"


@app.route('/')
def home() -> str:
    return render_template('index.html')


@app.route("/docs/")
@app.route("/docs/<path:filename>")
def docs(filename: str = "index.html"):
    return send_from_directory(DOCS_DIR, filename)


@app.route("/docs")
def docs_index_redirect() -> str:
    return send_from_directory(DOCS_DIR, "index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
