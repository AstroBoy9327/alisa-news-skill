# ------------------------------
# IMPORTS
# ------------------------------

from flask import Flask, request, jsonify
import feedparser
import requests
from bs4 import BeautifulSoup

# ------------------------------
# APP
# ------------------------------

app = Flask(__name__)

# ------------------------------
# RSS SOURCES
# ------------------------------

RSS_SOURCES = [
    "https://feeds.bbci.co.uk/mundo/rss.xml",
    "https://www.dw.com/es/rss",
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
]

# ------------------------------
# GET RSS NEWS
# ------------------------------

def get_rss_news(limit=3):
    news = []

    for rss_url in RSS_SOURCES:
        try:
            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:limit]:
                if hasattr(entry, "title"):
                    news.append(entry.title)

            if len(news) >= limit:
                break

        except Exception as e:
            print("RSS ERROR:", e)

    return news[:limit]

# ------------------------------
# GET ZERKALO NEWS
# ------------------------------

def get_zerkalo_news(limit=2):
    news = []

    try:
        response = requests.get(
            "https://smart.zerkalo.io/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )

        soup = BeautifulSoup(response.text, "html.parser")
        headlines = soup.find_all("h2")

        for h in headlines[:limit]:
            text = h.get_text(strip=True)
            if text:
                news.append(text)

    except Exception as e:
        print("ZERKALO ERROR:", e)

    return news

# ------------------------------
# MAIN ENDPOINT (ALISA)
# ------------------------------

@app.route("/", methods=["GET", "POST"])
def alisa_skill():

    # GET → para navegador / Render health check
    if request.method == "GET":
        return "OK", 200

    try:
        # Leer JSON seguro
        data = request.get_json(force=True, silent=True) or {}
        user_text = data.get("request", {}).get("original_utterance", "").lower()

        # SALUDO
        if user_text == "":
            text = "Здравствуйте. Я читаю глобальные новости из международных источников. Скажите: глобальные новости или зеркало."

        # AYUDA (OBLIGATORIO)
        elif "помощь" in user_text or "что ты умеешь" in user_text:
            text = "Я могу рассказать глобальные новости. Скажите: глобальные новости или зеркало."

        # LÓGICA PRINCIPAL
        else:
            news = get_rss_news(limit=3)

            if "зеркало" in user_text:
                news.extend(get_zerkalo_news(limit=2))

            if not news:
                text = "Извините, не удалось получить новости."
            else:
                text = "Вот международные новости из разных источников. " + ". ".join(news)

    except Exception as e:
        print("FATAL ERROR:", e)
        text = "Произошла ошибка при обработке запроса."

    # RESPUESTA FINAL (FORMATO YANDEX)
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