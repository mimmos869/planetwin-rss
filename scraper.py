from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import time
import urllib.parse

BOOKMAKERS = [
    {
        'name': 'PlanetWin365',
        'url': 'https://www.planetwin365.it/bonus/scommesse',
        'container': 'article.promo--item',
        'title': 'h2.promo--title',
        'description': 'div.promo--txt',
        'image': '.promo--img img',
        'link': '.promo--button button[title*="Dettagli"]'
    },
    {
        'name': 'StarVegas',
        'url': 'https://www.starvegas.it/promozioni/sport',
        'container': '.promo-section, .big-card-promotion',
        'title': '.promo-card-title',
        'description': '.promo-info',
        'image': '.promo-gradient',
        'link': '.btn-yellow, button.btn-yellow'
    },
    {
        'name': 'AdmiralBet',
        'url': 'https://www.admiralbet.it/promozioni/sport',
        'container': '.promo-section, .big-card-promotion',
        'title': '.promo-card-title',
        'description': '.promo-info',
        'image': '.promo-gradient',
        'link': '.btn-yellow, button.btn-yellow'
    },
    {
        'name': 'WilliamHill',
        'url': 'https://www.williamhill.it/promozioni',
        'container': '.promoCard',
        'title': '.promoCard__title',
        'description': '.promoCard__content p',
        'image': '.promoCard__img',
        'link': '.promoCard__cta'
    },
    {
        'name': 'NetBet',
        'url': 'https://scommesse.netbet.it/promozioni',
        'container': '.rettangolo-promo, .cg-promo-2',
        'title': '.titolo-promo',
        'description': '.info-promo',
        'image': '.img-fluid',
        'link': '.bottone-registrazione, a.bottone'
    },
    {
        'name': 'Lottomatica',
        'url': 'https://www.lottomatica.it/bonus/scommesse',
        'container': 'article.promo--item',
        'title': 'h2.promo--title',
        'description': '.promo--txt p',
        'image': '.promo--img img',
        'link': '.promo--button button[title*="Dettagli"]'
    },
    {
        'name': 'Sisal',
        'url': 'https://www.sisal.it/bonus/scommesse',
        'container': '.cardPromo, .cardPromo__status-active',
        'title': '.cardPromo__title',
        'description': '.cardPromo__subtitle',
        'image': '.cardPromo__imgContainer img',
        'link': '.card-button'
    },
    {
        'name': 'PokerStars',
        'url': 'https://www.pokerstars.it/bonus/scommesse',
        'container': '.cardPromo, .cardPromo__status-active',
        'title': '.cardPromo__title',
        'description': '.cardPromo__subtitle',
        'image': '.cardPromo__imgContainer img',
        'link': '.card-button'
    },
    {
        'name': 'SportBet',
        'url': 'https://www.sportbet.it/promo',
        'container': '.rettangolo-promo, .cg-promo-2',
        'title': '.titolo-promo span',
        'description': '.info-promo',
        'image': '.img-fluid',
        'link': '.rettangolo-promo'
    }
]

def scrape_bookmaker(driver, bookmaker):
    print(f"\n🎯 Scraping {bookmaker['name']}...")
    print(f"📍 URL: {bookmaker['url']}")
    
    try:
        driver.get(bookmaker['url'])
        print("⏳ Attendo caricamento pagina...")
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, bookmaker['container'])))
        
        time.sleep(3)
        
        promo_containers = driver.find_elements(By.CSS_SELECTOR, bookmaker['container'])
        print(f"🔍 Trovati {len(promo_containers)} elementi promo")
        
        promo_list = []
        for idx, container in enumerate(promo_containers, 1):
            try:
                # Titolo
                title_elem = container.find_element(By.CSS_SELECTOR, bookmaker['title'])
                title_text = title_elem.text.strip()
                
                print(f"  [{idx}] Elaborazione: {title_text}")
                
                # Descrizione
                try:
                    desc_elem = container.find_element(By.CSS_SELECTOR, bookmaker['description'])
                    description = desc_elem.text.strip()
                except:
                    description = ""
                
                # Immagine
                try:
                    if bookmaker['name'] in ['StarVegas', 'AdmiralBet']:
                        # Estrai da background-image
                        img_elem = container.find_element(By.CSS_SELECTOR, bookmaker['image'])
                        style = img_elem.get_attribute('style')
                        if 'background-image' in style:
                            img_url = style.split('url(')[1].split(')')[0].strip('"\'')
                        else:
                            img_url = ""
                    else:
                        img_elem = container.find_element(By.CSS_SELECTOR, bookmaker['image'])
                        img_url = img_elem.get_attribute('src')
                        if img_url and img_url.startswith('/'):
                            img_url = urllib.parse.urljoin(bookmaker['url'], img_url)
                except:
                    img_url = ""
                
                # Link
                try:
                    link_elem = container.find_element(By.CSS_SELECTOR, bookmaker['link'])
                    link = link_elem.get_attribute('href') or bookmaker['url']
                    if not link.startswith('http'):
                        link = urllib.parse.urljoin(bookmaker['url'], link)
                except:
                    link = bookmaker['url']
                
                if title_text and (title_text != "Promozione" or description):
                    promo_list.append({
                        'title': title_text,
                        'description': description,
                        'image': img_url,
                        'link': link,
                        'bookmaker': bookmaker['name'],
                        'pub_date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
                    })
                    print(f"      ✅ Aggiunta al feed")
                else:
                    print(f"      ⏭️  Saltata (contenuto vuoto)")
                    
            except Exception as e:
                print(f"      ❌ Errore: {e}")
                continue
        
        print(f"✅ {bookmaker['name']}: {len(promo_list)} promo estratte")
        return promo_list
        
    except Exception as e:
        print(f"❌ Errore scraping {bookmaker['name']}: {e}")
        return []

def scrape_all_bookmakers():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    print("🌐 Avvio browser...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    all_promos = []
    try:
        for bookmaker in BOOKMAKERS:
            promos = scrape_bookmaker(driver, bookmaker)
            all_promos.extend(promos)
            time.sleep(2)  # Pausa tra un sito e l'altro
        
    finally:
        driver.quit()
        print("🔒 Browser chiuso")
    
    return all_promos

def generate_rss(promos, output_file='promozioni.xml'):
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    
    ET.SubElement(channel, 'title').text = 'Promozioni Bookmaker Italia'
    ET.SubElement(channel, 'link').text = 'https://mimmos869.github.io/planetwin-rss/promozioni.xml'
    ET.SubElement(channel, 'description').text = 'Feed RSS unificato delle promozioni di tutti i bookmaker italiani'
    ET.SubElement(channel, 'language').text = 'it'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    for promo in promos:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = f"[{promo['bookmaker']}] {promo['title']}"
        ET.SubElement(item, 'category').text = promo['bookmaker']
        
        desc_html = f"<![CDATA["
        if promo['image']:
            desc_html += f"<img src='{promo['image']}' style='max-width:100%; height:auto;'/><br/><br/>"
        desc_html += f"<strong>{promo['bookmaker']}</strong><br/><br/>{promo['description']}]]>"
        ET.SubElement(item, 'description').text = desc_html
        
        if promo['image']:
            ET.SubElement(item, 'enclosure', url=promo['image'], type='image/jpeg')
        
        ET.SubElement(item, 'link').text = promo['link']
        ET.SubElement(item, 'pubDate').text = promo['pub_date']
        ET.SubElement(item, 'guid', isPermaLink='false').text = f"{promo['bookmaker']}_{promo['title']}_{promo['pub_date']}"
    
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent='  ')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"📄 Feed RSS generato: {output_file}")

if __name__ == '__main__':
    print("=" * 70)
    print("🎰 SCRAPER MULTI-BOOKMAKER ITALIA")
    print("=" * 70)
    print(f"📍 Monitoraggio {len(BOOKMAKERS)} bookmaker\n")
    
    try:
        all_promos = scrape_all_bookmakers()
        
        if all_promos:
            generate_rss(all_promos)
            print(f"\n🎉 PROCESSO COMPLETATO!")
            print(f"📊 Totale promozioni estratte: {len(all_promos)}")
            print(f"🏆 Bookmaker monitorati: {len(BOOKMAKERS)}")
        else:
            print("\n⚠️  Nessuna promozione trovata!")
            
    except Exception as e:
        print(f"\n❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()
