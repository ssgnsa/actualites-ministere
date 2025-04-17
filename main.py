import os
from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

def get_actualites():
    url = "https://web.construction.gouv.ci/index.php/actualites"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = []
    for item in soup.select(".item"):
        titre_tag = item.select_one("h4")
        lien_tag = item.select_one("a")
        image_tag = item.select_one("img")
        resume_tag = item.select_one("p")

        if not titre_tag or not lien_tag:
            continue

        titre = titre_tag.text.strip()
        lien = lien_tag["href"]
        image = image_tag["src"] if image_tag else ""
        resume = resume_tag.text.strip() if resume_tag else ""

        articles.append({
            "titre": titre,
            "lien": "https://web.construction.gouv.ci" + lien,
            "image": "https://web.construction.gouv.ci" + image if image else "",
            "resume": resume
        })
    return articles

def build_html(articles):
    html = '''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Actualités du Ministère</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body style="font-family: 'Open Sans', sans-serif;">
  <div class="container py-5">
    <h2 class="text-primary mb-4">📰 Dernières Actualités du Ministère</h2>
    <div class="row">
    '''

    for news in articles:
        html += f'''
      <div class="col-md-4 mb-4">
        <div class="card h-100 shadow-sm">
          {"<img src='" + news['image'] + "' class='card-img-top' alt='Image'>" if news['image'] else ""}
          <div class="card-body">
            <h5 class="card-title">{news['titre']}</h5>
            <p class="card-text">{news['resume']}</p>
            <a href="{news['lien']}" class="btn btn-primary" target="_blank">Lire la suite</a>
          </div>
        </div>
      </div>
    '''

    html += '''
    </div>
    <footer class="mt-5 text-center text-muted">
      Mise à jour : ''' + datetime.now().strftime("%d/%m/%Y %H:%M") + '''
    </footer>
  </div>
</body>
</html>'''
    return html

@app.route("/")
def home():
    articles = get_actualites()
    html = build_html(articles)
    return Response(html, mimetype='text/html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render fournit PORT automatiquement
    app.run(host="0.0.0.0", port=port)