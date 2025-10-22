import requests
from bs4 import BeautifulSoup

url = 'https://www.planetwin365.it/bonus/scommesse'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
print(f"Status code: {response.status_code}")
print(f"Lunghezza HTML: {len(response.text)} caratteri")

# Salva l'HTML per ispezionarlo
with open('debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

soup = BeautifulSoup(response.content, 'html.parser')
articles = soup.find_all('article')
print(f"Trovati {len(articles)} elementi <article>")

promo_items = soup.find_all('article', class_='promo--item')
print(f"Trovati {len(promo_items)} elementi con class='promo--item'")

# Cerca varianti
all_classes = soup.find_all(class_=lambda x: x and 'promo' in x.lower())
print(f"Trovati {len(all_classes)} elementi con 'promo' nel nome classe")

print("\nPrime 5 classi trovate:")
for i, elem in enumerate(all_classes[:5]):
    print(f"  {i+1}. {elem.get('class')}")
