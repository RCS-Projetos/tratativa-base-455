from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

def driver(headless=False):
    chrome_options = webdriver.ChromeOptions()
    if not headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    return webdriver.Chrome(options=chrome_options)

def wait(driver: webdriver.Chrome):
    return WebDriverWait(driver, 10)

def actions(driver: webdriver.Chrome):
    return ActionChains(driver)