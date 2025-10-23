import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_promos_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    print("🌐 Avvio browser...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("⏳ Attendo caricamento pagina...")
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.promo--item")))
        
        time.sleep(3)
        
        promos = driver.find_elements(By.CSS_SELECTOR, "article.promo--item")
        
        print(f"\n🔍 Trovati {len(promos)} elementi di promozione sulla pagina\n")
        
        promo_list = []
        for idx, promo in enumerate(promos, 1):
            try:
                title_elem = promo.find_element(By.CSS_SELECTOR, "h2.promo--title")
                title_text = title_elem.text.strip()
                
                print(f"  [{idx}] Elaborazione: {title_text}")
                
                desc_elem = promo.find_element(By.CSS_SELECTOR, "div.promo--txt")
                description = desc_elem.text.strip()
                
                img_elem = promo.find_element(By.TAG_NAME, "img")
                img_url = img_elem.get_attribute('src')
                
                promo_list.append({
                    'title': title_text,
                    'description': description,
                    'image': img_url,
                    'pub_date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
                })
                print(f"      ✅ Aggiunta al feed")
                    
            except Exception as e:
                print(f"      ❌ Errore: {e}")
                continue
        
        print(f"\n✅ Totale promozioni estratte con successo: {len(promo_list)}\n")
        return promo_list
        
    finally:
        driver.quit()
        print("🔒 Browser chiuso")

def generate_rss(promos, output_file='promozioni.xml'):
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
        
        desc_html = f"<![CDATA["
        if promo['image']:
            desc_html += f"<img src='{promo['image']}' style='max-width:100%; height:auto;'/><br/><br/>"
        desc_html += f"{promo['description']}]]>"
        ET.SubElement(item, 'description').text = desc_html
        
        if promo['image']:
            ET.SubElement(item, 'enclosure', url=promo['image'], type='image/jpeg')
        
        ET.SubElement(item, 'link').text = 'https://www.planetwin365.it/bonus/scommesse'
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
    except Exception as e:
        print(f"\n❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()
