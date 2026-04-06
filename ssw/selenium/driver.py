import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from ..functions.logger import Logger


class Driver:
    def __init__(self, headless: bool = True, download_dir: str = 'Downloads'):
        self._driver = webdriver.Chrome(options=self.options(headless, download_dir))
        self._wait = WebDriverWait(self._driver, 20)
        self._action = ActionChains(self._driver)

    def options(self, headless: bool = True, download_dir: str = 'Downloads'):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                self.logger.error(f"Error creating dir: {e}")

        return options

    def get(self, url: str):
        self._driver.get(url)

    def close(self):
        self._driver.close()

    def wait(self, wait: int = 10):
        return WebDriverWait(self._driver, wait)
    
    def wait_until(self, xpath:str):
        return self.wait().until(EC.presence_of_element_located((By.XPATH, xpath)))

    def actions(self):
        return ActionChains(self._driver)
    
    def execute_script(self, script: str, *args):
        self._driver.execute_script("arguments[0].value = arguments[1]", script, *args)

    def quit(self):
        self._driver.quit()

    def driver(self):
        return self._driver