import requests
from bs4 import BeautifulSoup

def search_amazon_products(query):
    url = f"https://www.amazon.fr/s?k={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for item in soup.select(".s-result-item")[:3]:
        title = item.select_one("h2 a span")
        img = item.select_one("img")
        link = item.select_one("h2 a")

        if title and link and img:
            results.append({
                "title": title.text.strip(),
                "image": img["src"],
                "link": "https://www.amazon.fr" + link["href"]
            })

    if not results:
        return "Aucun résultat trouvé sur Amazon.fr 😔"

    formatted = "\n\n".join([
        f"**{r['title']}**\n![obrazek]({r['image']})\n[Zobacz produkt]({r['link']})"
        for r in results
    ])
    return formatted