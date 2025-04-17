import os
from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def get_actualites():
    url = "https://web.construction.gouv.ci/index.php/actualites"

    # Configurer Selenium pour utiliser le navigateur Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Exécuter en mode sans tête
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    driver.implicitly_wait(10)  # Attendre 10 secondes pour que la page se charge

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erreur lors du chargement des actualités: {response.status_code}")
        return []

    # Analyser le contenu de la page
    soup = BeautifulSoup(response.content, "html.parser")

    # Vérification du contenu de la page
    print(f"Contenu de la page récupéré: {soup.prettify()[:500]}...")  # Afficher les 500 premiers caractères

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
