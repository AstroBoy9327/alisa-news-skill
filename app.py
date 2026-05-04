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
# RSS SOURCES (más activos)
# ------------------------------

RSS_SOURCES = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.cnn.com/rss/edition.rss",
    "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"
]

# ------------------------------
# GET RSS NEWS
# ------------------------------

def get_rss_news(limit=3):
    news = []

    for rss_url in RSS_SOURCES:
        try:
            feed = feedparser.parse(rss_url)

            entries = feed.entries
            random.shuffle(entries)  # evitar repetir siempre lo mismo

            for entry in entries:
                if hasattr(entry, "title"):
                    news.append(entry.title)

                if len(news) >= limit:
                    return news

        except Exception as e:
            print("RSS ERROR:", e)

    return news[:limit]

# ------------------------------
# GET ZERKALO NEWS
# ------------------------------

def get_zerkalo_news(limit=3):
    news = []

    try:
        response = requests.get(
            "https://zerkalo.io/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=3
        )

        soup = BeautifulSoup(response.text, "html.parser")

        # Selector más controlado (puede ajustarse si cambia la web)
        headlines = soup.select("a span")

        for h in headlines:
            text = h.get_text(strip=True)

            if text and len(text) > 30:
                news.append(text)

            if len(news) >= limit:
                break

    except Exception as e:
        print("ZERKALO ERROR:", e)

    return news

# ------------------------------
# MAIN ENDPOINT (ALISA)
# ------------------------------

@app.route("/", methods=["GET", "POST"])
def alisa_skill():

    # GET → health check
    if request.method == "GET":
        return "OK", 200

    try:
        data = request.get_json(force=True, silent=True) or {}
        user_text = data.get("request", {}).get("original_utterance", "").lower()

        # SALUDO
        if user_text == "":
            text = "Здравствуйте. Я читаю глобальные новости. Скажите: глобальные новости или зеркало."

        # AYUDA
        elif "помощь" in user_text or "что ты умеешь" in user_text:
            text = "Я могу рассказать глобальные новости. Скажите: глобальные новости или зеркало."

        # ZERKALO PRIORIDAD SOLO SI LO PIDEN
        elif "зеркало" in user_text:
            news = get_zerkalo_news(limit=3)

            if not news:
                news = get_rss_news(limit=3)

            if not news:
                text = "Не удалось получить новости."
            else:
                text = "Новости с сайта Зеркало. " + ". ".join(news)

        # DEFAULT → RSS
        else:
            news = get_rss_news(limit=3)

            if not news:
                text = "Не удалось получить новости."
            else:
                text = "Вот международные новости. " + ". ".join(news)

    except Exception as e:
        print("FATAL ERROR:", e)
        text = "Произошла ошибка при обработке запроса."

    # RESPUESTA YANDEX
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
# RUN LOCAL
# ------------------------------

if __name__ == "__main__":
    app.run(port=5000)