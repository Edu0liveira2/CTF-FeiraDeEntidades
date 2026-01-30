from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from screenTimer import screenTimer
import threading
import json
import os

app = Flask(__name__)

# ================== CONFIG ==================

SCOREBOARD_FILE = "scoreboard.json"

FLAGS_VALIDAS = {
    "FLAG{inspect_element_is_your_friend}": "CTF Fácil",
    "FLAG{frontend_is_not_security}": "CTF Médio",
    "FLAG{cookies_are_not_auth}": "CTF Difícil"
}

current_timer = None
time_up = False

# ================== SCOREBOARD ==================

def load_scoreboard():
    if not os.path.exists(SCOREBOARD_FILE):
        return []
    try:
        with open(SCOREBOARD_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except json.JSONDecodeError:
        return []

def save_scoreboard(data):
    with open(SCOREBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

scoreboard = load_scoreboard()

# ================== TIMER ==================

def start_timer(duration):
    global current_timer, time_up

    if current_timer is not None:
        return

    time_up = False

    def acabou():
        global current_timer, time_up
        time_up = True
        current_timer = None
        print("tempo acabou")

    current_timer = screenTimer(duration, acabou)
    threading.Thread(target=current_timer.start, daemon=True).start()

def stop_timer():
    global current_timer
    if current_timer:
        current_timer.stop()
        current_timer = None

# ================== ROUTES ==================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/time_status")
def time_status():
    return jsonify({"time_up": time_up})

@app.route("/submit", methods=["POST"])
def submit_flag():
    flag = request.form.get("flag", "").strip()

    if flag not in FLAGS_VALIDAS:
        return render_template("result.html", success=False)

    elapsed = None
    if current_timer:
        elapsed = current_timer.get_elapsed()
        stop_timer()

    response = make_response(
        render_template(
            "result.html",
            success=True,
            flag=flag,
            challenge=FLAGS_VALIDAS[flag],
            elapsed=elapsed
        )
    )

    # reset do cookie do CTF difícil
    response.delete_cookie("role", path="/")
    response.set_cookie("role", "user", path="/")

    return response

@app.route("/register", methods=["POST"])
def register_score():
    name = request.form.get("name", "").strip()
    flag = request.form.get("flag")
    elapsed = int(request.form.get("elapsed"))

    if not name or flag not in FLAGS_VALIDAS:
        return redirect(url_for("index"))

    scoreboard.append({
        "name": name,
        "challenge": FLAGS_VALIDAS[flag],
        "time": elapsed
    })

    scoreboard.sort(key=lambda x: x["time"])
    save_scoreboard(scoreboard)

    return render_template("scoreboard.html", scoreboard=scoreboard)

# ================== CTFs ==================

@app.route("/ctf1")
def ctf1():
    if current_timer is None:
        start_timer(5*60)
    return render_template("ctf1.html")

@app.route("/ctf2")
def ctf2():
    if current_timer is None:
        start_timer(10*60)
    return render_template("ctf2.html")

@app.route("/ctf3")
def ctf3():
    if current_timer is None:
        start_timer(15*60)

    role = request.cookies.get("role", "user")

    if role == "admin":
        return render_template("ctf3.html", is_admin=True)

    response = make_response(
        render_template("ctf3.html", is_admin=False)
    )
    response.delete_cookie("role", path="/")
    response.set_cookie("role", "user", path="/")
    return response

# ================== SCOREBOARD ==================

@app.route("/scoreboard")
def show_scoreboard():
    return render_template("scoreboard.html", scoreboard=scoreboard)

# ================== MAIN ==================

if __name__ == "__main__":
    app.run(debug=True)
