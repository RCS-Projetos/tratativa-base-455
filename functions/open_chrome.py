import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def driver(headless=True):
    chrome_options = webdriver.ChromeOptions()
    
    # --- 1. CONFIGURAÇÕES OBRIGATÓRIAS PARA DOCKER ---
    # --headless=new é a versão nova do Chrome, muito mais estável que a antiga
    chrome_options.add_argument('--headless=new') 
    chrome_options.add_argument('--no-sandbox') # Crucial para rodar como root/docker
    chrome_options.add_argument('--disable-dev-shm-usage') # Evita crash de memória
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # --- 2. PASTA DE DOWNLOAD CONTROLADA ---
    # Em vez de usar '~' (que varia), usamos a pasta onde o robô está rodando (/app)
    # Isso garante que temos permissão de escrita.
    download_folder = os.path.join(os.getcwd(), 'downloads')

    if not os.path.exists(download_folder):
        os.makedirs(download_folder, exist_ok=True)
        # Dá permissão total na pasta para garantir que o Chrome consiga escrever
        try:
            os.chmod(download_folder, 0o777)
        except:
            pass

    print(f"DEBUG: Pasta de Downloads configurada para: {download_folder}")

    # --- 3. PREFERÊNCIAS DO CHROME ---
    prefs = {
        "download.default_directory": download_folder,
        "download.prompt_for_download": False, # Não perguntar "onde salvar?"
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Inicia o Driver
    try:
        service = Service(ChromeDriverManager().install())
        driver_instance = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"ERRO CRÍTICO AO INICIAR DRIVER: {e}")
        raise e

    # --- 4. O COMANDO MÁGICO (CDP) ---
    # Isso é o que faltava! Força o Chrome Headless a permitir downloads.
    # Sem isso, ele clica no botão e nada acontece.
    driver_instance.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": download_folder
    })

    return driver_instance

def wait(driver: webdriver.Chrome):
    return WebDriverWait(driver, 10)

def actions(driver: webdriver.Chrome):
    return ActionChains(driver)