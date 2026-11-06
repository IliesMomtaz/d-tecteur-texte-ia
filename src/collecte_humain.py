import pandas as pd
import requests
import time 
from pathlib import Path

HEADERS = {"User-Agent" : "DetecteurTexteIA/0.1 (Ilies.momtaz@outlook.fr)"}
URL = "https://fr.wikipedia.org/w/api.php"


def trouver_revid(titre):
    """cette fonction va demander a Wikipedia quelle était la derniere version de l'article avant le 31/12/2021
    puis elle renvoie son revid et sa date, elle renvoie aussi None si l'article n'existait pas a cette époque"""
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": titre,
        "rvlimit": "1",
        "rvstart": "2021-12-31T23:59:59Z",
        "rvdir": "older",
        "rvprop": "ids|timestamp",
        "redirects": "1",
        "format": "json",
        "formatversion": "2",
    }
    reponse = requests.get(URL, params=params, headers=HEADERS, timeout=10)
    reponse.raise_for_status()
    donnees = reponse.json()

    page = donnees["query"]["pages"][0]
    revisions = page.get("revisions")

    if revisions is None:
        return None

    revision = revisions[0]
    return revision["revid"], revision["timestamp"]

def recuperer_html(revid):
    """prend revid et télécharge le contenu de la page html associé"""
    params = {
              "action" : "parse", 
              "oldid" : revid, 
              "prop": "text", 
              "disableeditsection" : "1",
              "format" : "json",
              "formatversion" : "2"
            }

    reponse = requests.get(URL, params=params, headers=HEADERS, timeout=10)
    reponse.raise_for_status()
    donnees = reponse.json()
    return donnees["parse"]["text"]

sujets = pd.read_csv("data/sujets.csv")
resultats = []
echecs = []

for ligne in sujets.itertuples():
    infos = trouver_revid(ligne.titre)

    if infos is None : 
        echecs.append(ligne.titre)
        continue
    revid, date = infos
    html = recuperer_html(revid)
    resultats.append({
                    "theme" : ligne.theme, 
                    "titre" : ligne.titre,
                    "revid" : revid,
                    "date" : date,
                    "html" : html
                    })
    print(f"OK : {ligne.titre}")
    time.sleep(0.5)

Path("data/raw").mkdir(parents=True, exist_ok=True)
pd.DataFrame(resultats).to_csv("data/raw/humains_bruts.csv", index=False)
print(len(resultats))
print(len(echecs))
for i in echecs:
    print(echecs[i])
