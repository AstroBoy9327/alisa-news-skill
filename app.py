# ------------------------------
# IMPORTS
# ------------------------------

from flask import Flask, request, jsonify
import feedparser
import random

# ------------------------------
# APP
# ------------------------------

app = Flask(__name__)

# ------------------------------
# RSS SOURCES (RUSO - ESTABLE)
# ------------------------------

RSS_SOURCES = [
    "https://meduza.io/rss/all",              # Principal
    "https://www.svoboda.org/api/z-pq_iqgy_pp",
    "https://www.dw.com/russian/rss"
]

# ------------------------------
# OBTENER NOTICIAS DESDE RSS
# ------------------------------

def get_rss_news(limit=3):
    news = []

    for rss_url in RSS_SOURCES:
        try:
            feed = feedparser.parse(rss_url)
            entries = feed.entries

            # Mezclar para evitar repetir siempre lo mismo
            random.shuffle(entries)

            for entry in entries:
                title = getattr(entry, "title", "").strip()

                if title and title not in news:
                    news.append(title)

                if len(news) >= limit:
                    return news

        except Exception as e:
            print("RSS ERROR:", e)

    return news[:limit]

# ------------------------------
# ENDPOINT PRINCIPAL (ALISA)
# ------------------------------

@app.route("/", methods=["GET", "POST"])
def alisa_skill():

    # Health check (Render / navegador)
    if request.method == "GET":
        return "OK", 200

    try:
        data = request.get_json(force=True, silent=True) or {}
        user_text = data.get("request", {}).get("original_utterance", "").lower()

        # SALUDO
        if user_text == "":
            text = "Здравствуйте. Я озвучиваю последние международные новости на русском языке. Скажите: новости."

        # AYUDA (IMPORTANTE PARA YANDEX)
        elif "помощь" in user_text or "что ты умеешь" in user_text:
            text = "Я могу рассказать последние новости. Просто скажите: новости."

        # NOTICIAS
        else:
            news = get_rss_news(limit=3)

            if not news:
                text = "Не удалось получить новости. Попробуйте позже."
            else:
                text = "Вот последние новости. " + ". ".join(news)

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