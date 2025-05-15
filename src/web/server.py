from flask import Flask, send_from_directory
from flask_sock import Sock

app = Flask(__name__, static_folder="static", static_url_path="/")

@app.route("/")
def index(path=None):
    if not path or path == "/" or path == "index.html":
        return send_from_directory("static", "index.html")
    else:
        return send_from_directory("static", path)

if __name__ == '__main__':
    # Start the API Server
    # api.run(host="0.0.0.0", port=7750)
    app.run(port=7750)