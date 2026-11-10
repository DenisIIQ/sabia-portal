import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

APP_URLS = [
    "https://sabia-tutores.streamlit.app/"
]

def wake_app(url):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    try:
        # O Selenium 4.6+ gerencia o driver automaticamente
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        try:
            button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'Yes, get this app back up')]")
                )
            )
            button.click()
            wait.until(
                EC.invisibility_of_element_located(
                    (By.XPATH, "//button[contains(text(),'Yes, get this app back up')]")
                )
            )
            print(f"App acordado: {url}")
        except TimeoutException:
            print(f"App já acordado ou tempo de espera excedido: {url}")
    except Exception as e:
        print(f"Ocorreu um erro ao tentar acordar o app: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    for app_url in APP_URLS:
        wake_app(app_url)