

# ------------------------------
# IMPORTAMOS LIBRERÍAS
# ------------------------------

from flask import Flask, request, jsonify
import feedparser              # Para leer RSS
import requests                # Para descargar páginas web
from bs4 import BeautifulSoup  # Para hacer scraping HTML

# ------------------------------
# CREAMOS LA APLICACIÓN FLASK
# ------------------------------

app = Flask(__name__)

# ------------------------------
# FUENTES DE NOTICIAS CON RSS (PRIORIDAD)
# ------------------------------

RSS_SOURCES = [
    "https://feeds.bbci.co.uk/mundo/rss.xml",          # BBC Mundo
    "https://www.dw.com/es/rss",                       # Deutsche Welle
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
]

# ------------------------------
# FUNCIÓN: LEER NOTICIAS DESDE RSS
# ------------------------------

def get_rss_news(limit=3):
    """
    Lee titulares desde varias fuentes RSS.
    Devuelve una lista de strings (titulares).
    """
    news = []

    for rss_url in RSS_SOURCES:
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:limit]:
            news.append(entry.title)

        # Si ya tenemos suficientes noticias, paramos
        if len(news) >= limit:
            break

    return news[:limit]

# ------------------------------
# FUNCIÓN: SCRAPING SIMPLE DE ZERKALO
# ------------------------------

def get_zerkalo_news(limit=2):
    """
    Descarga la página de smart.zerkalo.io
    y extrae algunos titulares visibles.
    """
    news = []

    try:
        response = requests.get(
            "https://smart.zerkalo.io/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )

        soup = BeautifulSoup(response.text, "html.parser")

        # Buscamos encabezados (esto puede cambiar si la web cambia)
        headlines = soup.find_all("h2")

        for h in headlines[:limit]:
            text = h.get_text(strip=True)
            if text:
                news.append(text)

    except Exception:
        pass  # Si falla, simplemente no devuelve noticias de Zerkalo

    return news

# ------------------------------
# ENDPOINT PRINCIPAL (ALISA LLAMA AQUÍ)
# ------------------------------

@app.route("/", methods=["GET", "POST"])
def alisa_skill():

    # ✅ Para navegador / Render
    if request.method == "GET":
        return "OK"

    # Obtenemos el texto del usuario
    data = request.get_json()
    user_text = data.get("request", {}).get("original_utterance", "").lower()

    # ✅ SALUDO
    if user_text == "":
        text = "Здравствуйте. Я читаю глобальные новости из международных источников. Скажите: глобальные новости или зеркало."

    # ✅ AYUDA (OBLIGATORIO para Yandex)
    elif "помощь" in user_text or "что ты умеешь" in user_text:
        text = "Я могу рассказать глобальные новости. Скажите: глобальные новости или зеркало."

    else:
        # Noticias RSS
        news = get_rss_news(limit=3)

        # Si menciona Zerkalo
        if "зеркало" in user_text:
            zerkalo_news = get_zerkalo_news(limit=2)
            news.extend(zerkalo_news)

        if not news:
            text = "Извините, не удалось получить новости."
        else:
            text = "Вот глобальные новости. " + ". ".join(news)

    # Respuesta para Alisa
    response = {
        "response": {
            "text": text,
            "tts": text,
            "end_session": False
        },
        "version": "1.0"
    }

    return jsonify(response)

# ------------------------------
# EJECUCIÓN LOCAL (SOLO PARA PRUEBAS)
# ------------------------------

if __name__ == "__main__":
    app.run(port=5000)
