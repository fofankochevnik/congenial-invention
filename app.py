from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

cache = {"level": "неизвестен", "updated": 0}

def get_level():
    if time.time() - cache["updated"] < 60:
        return cache["level"]
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://bplarussia.ru/region/lipeckaya-oblast/", headers=headers, timeout=4)
        soup = BeautifulSoup(r.text, "html.parser")
        posts = soup.find_all("h2")
        real = [p.text.strip() for p in posts if p.text.strip() not in ("Регионы", "Фильтры")]
        latest = real[0] if real else ""
        level = "зелёный" if "отбой" in latest.lower() else "красный"
        cache["level"] = level
        cache["updated"] = time.time()
        return level
    except:
        return cache["level"]

def make_response(text, end=True):
    return jsonify({
        "version": "1.0",
        "response": {
            "text": text,
            "tts": text,
            "end_session": end
        }
    })

@app.route("/alice", methods=["POST"])
def alice():
    body = request.json
    is_new = body.get("session", {}).get("new", False)
    command = body.get("request", {}).get("command", "").lower()

    if any(w in command for w in ["помощь", "что ты умеешь", "команды"]):
        return make_response(
            "Я умею показывать текущий уровень угрозы БПЛА в Липецке. "
            "Команды: скажи какая сейчас опасность бпла, "
            "скажи какой уровень угрозы, "
            "скажи уровень угрозы атаки бпла.",
            end=False
        )

    level = get_level()
    if is_new and not command:
        return make_response(
            f"Сейчас {level} уровень опасности БПЛА в Липецкой области. "
            "Чтобы обновить или уточнить, скажите: уровень угрозы. "
            "Для списка команд скажите помощь.",
            end=False
        )

    return make_response(f"Сейчас {level} уровень опасности БПЛА в Липецкой области.")

@app.route("/ping")
def ping():
    return "ok"

@app.route("/")
def index():
    return "", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
