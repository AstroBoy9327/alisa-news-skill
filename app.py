

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

@app.route("/", methods=["POST"])
def alisa_skill():
    """
    Esta función se ejecuta cuando Alisa llama a la skill.
    """

    # Obtenemos el texto que dijo el usuario
    data = request.get_json()
    user_text = data.get("request", {}).get("original_utterance", "").lower()

    # Noticias principales (RSS)
    news = get_rss_news(limit=3)

    # Si el usuario menciona Zerkalo, añadimos scraping
    if "зеркало" in user_text:
        zerkalo_news = get_zerkalo_news(limit=2)
        news.extend(zerkalo_news)

    # Si no se pudo obtener nada
    if not news:
        text = "Извините, не удалось получить новости."
    else:
        text = "Вот международные новости. " + ". ".join(news)

    # RESPUESTA EN FORMATO QUE ALISA ENTIENDE
    response = {
        "response": {
            "text": text,
            "tts": text,
            "end_session": True
        },
        "version": "1.0"
    }

    return jsonify(response)

# ------------------------------
# EJECUCIÓN LOCAL (SOLO PARA PRUEBAS)
# ------------------------------

if __name__ == "__main__":
    app.run(port=5000)
