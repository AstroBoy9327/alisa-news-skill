# ------------------------------
# IMPORTAMOS LIBRERÍAS
# ------------------------------

from flask import Flask, request, jsonify
import feedparser
import requests
from bs4 import BeautifulSoup

# ------------------------------
# APP FLASK
# ------------------------------

app = Flask(__name__)

# ------------------------------
# FUENTES RSS
# ------------------------------

RSS_SOURCES = [
    "https://feeds.bbci.co.uk/mundo/rss.xml",
    "https://www.dw.com/es/rss",
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
]

# ------------------------------
# RSS NEWS
# ------------------------------

def get_rss_news(limit=3):
    news = []

    for rss_url in RSS_SOURCES:
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:limit]:
            news.append(entry.title)

        if len(news) >= limit:
            break

    return news[:limit]

# ------------------------------
# ZERKALO SCRAPING
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

    except Exception:
        pass

    return news

# ------------------------------
# ENDPOINT ALISA
# ------------------------------

@app.route("/", methods=["GET", "POST"])
def alisa_skill():

    # ✔️ GET para navegador / Render
    if request.method == "GET":
        return "OK"

    # ✔️ Manejo seguro del JSON
    data = request.get_json(silent=True)

    if not data:
        user_text = ""
    else:
        user_text = data.get("request", {}).get("original_utterance", "").lower()

    # ✔️ SALUDO
    if user_text == "":
        text = "Здравствуйте. Я читаю глобальные новости из международных источников. Скажите: глобальные новости или зеркало."

    # ✔️ AYUDA (REQUERIDO POR YANDEX)
    elif "помощь" in user_text or "что ты умеешь" in user_text:
        text = "Я могу рассказать глобальные новости. Скажите: глобальные новости или зеркало."

    # ✔️ LÓGICA PRINCIPAL
    else:
        news = get_rss_news(limit=3)

        if "зеркало" in user_text:
            zerkalo_news = get_zerkalo_news(limit=2)
            news.extend(zerkalo_news)

        if not news:
            text = "Извините, не удалось получить новости."
        else:
            text = "Вот международные новости из разных источников. " + ". ".join(news)
    # ✔️ SEGURIDAD EXTRA (anti-crash)
    if not text:
        text = "Ошибка обработки запроса."

    

    return jsonify(response)

# ------------------------------
# LOCAL RUN
# ------------------------------

if __name__ == "__main__":
    app.run(port=5000)