from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import datetime
from btcmonitor import AzureBlobStorage, BTCMonitor
import tempfile
import shutil

def main():
    temp_dir = tempfile.mkdtemp()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")

    azblobstorage = AzureBlobStorage(os.getenv('AZURE_STORAGE_CONNECTION_STRING'), 'btcmonitor', './data/logs.txt')
    btcmonitor = BTCMonitor(10, azblobstorage)

    btcmonitor.start()

    locator = (By.CSS_SELECTOR, "div.text-4xl.lg\:text-5xl.inline-block.relative.tabular-nums")
    driver = webdriver.Chrome(chrome_options)
    try:
        driver.get('https://www.coindesk.com/price/bitcoin')
        div_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(locator)
        )
        while True:
            div_container = driver.find_element(*locator)
            html = div_container.get_attribute('outerHTML')
            soup = BeautifulSoup(html, 'html.parser')
            value = soup.find('div', class_="text-4xl lg:text-5xl inline-block relative tabular-nums").contents[0].strip()
            percentage = soup.find('span', class_="font-medium").text.strip()
            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
            p_sign = '+' if soup.find('svg', class_="w-[25px] h-[25px]").path.attrs['fill'] == '#10A05F' else '-'
            line = f'{value};{p_sign}{percentage};{timestamp}\n'
            btcmonitor.add_event(line)
            WebDriverWait(driver, 10).until(
                lambda driver: BeautifulSoup(driver.find_element(*locator).get_attribute('outerHTML'), 'html.parser').find('div', class_="text-4xl lg:text-5xl inline-block relative tabular-nums").contents[0].strip() != value
            )
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    finally:
        driver.quit()
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    main()
    
