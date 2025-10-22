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

def scrape_promos_selenium(url):
    """Scrape delle promozioni usando Selenium"""
    
    # Configurazione Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Esegui senza aprire finestra
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    print("🌐 Avvio browser...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("⏳ Attendo caricamento pagina...")
        
        # Aspetta che gli elementi delle promo si carichino
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.promo--item, article[class*='promo']")))
        
        # Aspetta un po' per il caricamento dinamico
        time.sleep(3)
        
        # Trova tutti gli articoli delle promo
        promos = driver.find_elements(By.CSS_SELECTOR, "article.promo--item, article[class*='promo']")
        
        print(f"\n🔍 Trovati {len(promos)} elementi di promozione sulla pagina\n")
        
        promo_list = []
        for idx, promo in enumerate(promos, 1):
            try:
                # Estrai titolo
                try:
                    title_elem = promo.find_element(By.CSS_SELECTOR, "h2.promo--title, h2[class*='title']")
                    title_text = title_elem.text.strip()
                except:
                    title_text = "Promozione"
                
                print(f"  [{idx}] Elaborazione: {title_text}")
                
                # Estrai descrizione
                try:
                    desc_elem = promo.find_element(By.CSS_SELECTOR, "div.promo--txt, div[class*='txt'], div[class*='description']")
                    description = desc_elem.text.strip()
                except:
                    description = ""
                
                # Estrai immagine
                try:
                    img_elem = promo.find_element(By.TAG_NAME, "img")
                    img_url = img_elem.get_attribute('src')
                except:
                    img_url = ""
                
                # Estrai link (se disponibile)
                try:
                    link_elem = promo.find_element(By.CSS_SELECTOR, "a, button[title*='Dettagli']")
                    link = link_elem.get_attribute('href') or url
                except:
                    link = url
                
                if title_text != "Promozione" or description:  # Aggiungi solo se ha contenuto
                    promo_list.append({
                        'title': title_text,
                        'description': description,
                        'image': img_url,
                        'link': link,
                        'pub_date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
                    })
                    print(f"      ✅ Aggiunta al feed")
                else:
                    print(f"      ⏭️  Saltata (contenuto vuoto)")
                    
            except Exception as e:
                print(f"      ❌ Errore: {e}")
                continue
        
        print(f"\n✅ Totale promozioni estratte con successo: {len(promo_list)}\n")
        return promo_list
        
    finally:
        driver.quit()
        print("🔒 Browser chiuso")

def generate_rss(promos, output_file='promozioni.xml'):
    """Genera il feed RSS"""
    
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    
    ET.SubElement(channel, 'title').text = 'Promozioni PlanetWin365'
    ET.SubElement(channel, 'link').text = 'https://www.planetwin365.it/bonus/scommesse'
    ET.SubElement(channel, 'description').text = 'Feed RSS delle ultime promozioni scommesse'
    ET.SubElement(channel, 'language').text = 'it'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    for promo in promos:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = promo['title']
        
        # Descrizione con immagine
        desc_html = f"<![CDATA["
        if promo['image']:
            desc_html += f"<img src='{promo['image']}' style='max-width:100%; height:auto;'/><br/><br/>"
        desc_html += f"{promo['description']}]]>"
        ET.SubElement(item, 'description').text = desc_html
        
        ET.SubElement(item, 'link').text = promo['link']
        ET.SubElement(item, 'pubDate').text = promo['pub_date']
        ET.SubElement(item, 'guid', isPermaLink='false').text = f"{promo['title']}_{promo['pub_date']}"
    
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent='  ')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"📄 Feed RSS generato: {output_file}")

if __name__ == '__main__':
    URL = 'https://www.planetwin365.it/bonus/scommesse'
    
    print("=" * 60)
    print("🎰 SCRAPER PROMOZIONI PLANETWIN365")
    print("=" * 60)
    print(f"📍 URL: {URL}\n")
    
    try:
        promos = scrape_promos_selenium(URL)
        
        if promos:
            generate_rss(promos)
            print("\n🎉 Processo completato con successo!")
        else:
            print("\n⚠️  Nessuna promozione trovata!")
            print("Possibili cause:")
            print("  - La pagina non contiene promozioni al momento")
            print("  - La struttura HTML è cambiata")
            print("  - Protezioni anti-bot troppo forti")
    except Exception as e:
        print(f"\n❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()