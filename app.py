# ------------------------------
# IMPORTS
# ------------------------------

from flask import Flask, request, jsonify
import feedparser
import requests
from bs4 import BeautifulSoup
import random

# ------------------------------
# APP
# ------------------------------

app = Flask(__name__)

# ------------------------------
# RSS (fallback)
# ------------------------------

RSS_SOURCES = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.cnn.com/rss/edition.rss"
]

# ------------------------------
# RSS NEWS
# ------------------------------

def get_rss_news(limit=3):
    news = []

    for rss_url in RSS_SOURCES:
        try:
            feed = feedparser.parse(rss_url)
            entries = feed.entries
            random.shuffle(entries)

            for entry in entries:
                if hasattr(entry, "title"):
                    news.append(entry.title)

                if len(news) >= limit:
                    return news

        except Exception as e:
            print("RSS ERROR:", e)

    return news[:limit]

# ------------------------------
# ZERKALO (PRIORIDAD)
# ------------------------------

def get_zerkalo_news(limit=3):
    news = []

    try:
        response = requests.get(
            "https://zerkalo.io/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=2.5  # 🔥 clave para no fallar en moderación
        )

        soup = BeautifulSoup(response.text, "html.parser")

        # 🔥 selector más amplio (evita quedarte sin datos)
        headlines = soup.find_all(["h1", "h2", "h3"])

        for h in headlines:
            text = h.get_text(strip=True)

            if text and len(text) > 25:
                news.append(text)

            if len(news) >= limit:
                break

    except Exception as e:
        print("ZERKALO ERROR:", e)

    return news

# ------------------------------
# MAIN ENDPOINT
# ------------------------------

@app.route("/", methods=["GET", "POST"])
def alisa_skill():

    if request.method == "GET":
        return "OK", 200

    try:
        data = request.get_json(force=True, silent=True) or {}
        user_text = data.get("request", {}).get("original_utterance", "").lower()

        # SALUDO
        if user_text == "":
            text = "Здравствуйте. Я читаю новости. Скажите: новости или зеркало."

        # AYUDA
        elif "помощь" in user_text:
            text = "Я могу рассказать новости. Скажите: зеркало или новости."

        else:
            # 🔥 INTENTA ZERKALO PRIMERO SIEMPRE
            news = get_zerkalo_news(limit=3)

            # 🔥 FALLBACK SI FALLA
            if not news:
                news = get_rss_news(limit=3)

            if not news:
                text = "Не удалось получить новости."
            else:
                text = "Вот последние новости. " + ". ".join(news)

    except Exception as e:
        print("FATAL ERROR:", e)
        text = "Произошла ошибка."

    response = {
        "response": {
            "text": text,
            "tts": text,
            "end_session": False
        },
        "version": "1.0"
    }

    return jsonify(response), 200

# ------------------------------
# RUN
# ------------------------------

if __name__ == "__main__":
    app.run(port=5000)