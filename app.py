from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_level():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://bplarussia.ru/region/lipeckaya-oblast/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        posts = soup.find_all("h2")
        real = [p.text.strip() for p in posts if p.text.strip() not in ("Регионы", "Фильтры")]
        latest = real[0] if real else ""
        if "отбой" in latest.lower():
            return "зелёный"
        return "красный"
    except:
        return "неизвестен"

@app.route("/alice", methods=["POST"])
def alice():
    level = get_level()
    text = f"Сейчас {level} уровень опасности БПЛА в Липецкой области."
    return jsonify({
        "version": "1.0",
        "response": {
            "text": text,
            "tts": text,
            "end_session": True
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)