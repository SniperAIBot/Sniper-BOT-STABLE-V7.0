from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route("/")
def home():
    return "SNIPER BOT RUNNING"


def run_health_server():

    thread = Thread(
        target=lambda: app.run(
            host="0.0.0.0",
            port=8080
        )
    )

    thread.daemon = True

    thread.start()
