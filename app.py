from flask import Flask, render_template, request
from screenTimer import screenTimer
import threading
import time
import json
import os

app = Flask(__name__)

SCOREBOARD_FILE = "scoreboard.json"

FLAGS_VALIDAS = {
    "FLAG{inspect_element_is_your_friend}": "CTF Fácil",
    "FLAG{frontend_is_not_security}": "CTF Difícil"
}

current_timer = None

def load_scoreboard():
    if not os.path.exists(SCOREBOARD_FILE):
        return []

    try:
        with open(SCOREBOARD_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []

def save_scoreboard(data):
    with open(SCOREBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

scoreboard = load_scoreboard()

def start_timer(duration):
    global current_timer

    def acabou():
        print("tempo acabou")

    # cria o objeto IMEDIATAMENTE
    current_timer = screenTimer(duration, acabou)

    # só o mainloop roda na thread
    threading.Thread(
        target=current_timer.start,
        daemon=True
    ).start()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_flag():
    global current_timer

    flag = request.form.get("flag", "").strip()

    if flag not in FLAGS_VALIDAS:
        return render_template("result.html", success=False)

    elapsed = None
    if current_timer:
        elapsed = current_timer.get_elapsed()
        current_timer.stop()
        current_timer = None

    return render_template(
        "result.html",
        success=True,
        flag=flag,
        challenge=FLAGS_VALIDAS[flag],
        elapsed=elapsed
    )

@app.route("/register", methods=["POST"])
def register_score():
    name = request.form.get("name", "").strip()
    flag = request.form.get("flag")
    elapsed = int(request.form.get("elapsed"))

    if not name or flag not in FLAGS_VALIDAS:
        return render_template("result.html", success=False)

    entry = {
        "name": name,
        "challenge": FLAGS_VALIDAS[flag],
        "time": elapsed
    }

    scoreboard.append(entry)
    scoreboard.sort(key=lambda x: x["time"])
    save_scoreboard(scoreboard)

    return render_template("scoreboard.html", scoreboard=scoreboard)

@app.route("/ctf1")
def ctf1():
    start_timer(5 * 60)
    return render_template("ctf1.html")

@app.route("/ctf2")
def ctf2():
    start_timer(10 * 60)
    return render_template("ctf2.html")

@app.route("/flag2")
def flag2():
    return render_template("flag2.html")

@app.route("/scoreboard")
def show_scoreboard():
    return render_template("scoreboard.html", scoreboard=scoreboard)

if __name__ == "__main__":
    app.run(debug=True)
