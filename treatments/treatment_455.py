import os
import time
from datetime import timedelta
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from functions import open_page_156
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('URL_455')

def treat_455(driver: Chrome):
    wait = WebDriverWait(driver, 20)
    
    try:
        driver.get(url)
        
        data_final = datetime.now().strftime("%d%m%y")
        data_inicial = (datetime.now() - timedelta(days=31)).strftime("%d%m%y")

        campos = [
            # ("/html/body/form/input[2]", filial),
            ("/html/body/form/input[10]", data_inicial),
            ("/html/body/form/input[11]", data_final),
            ("/html/body/form/input[20]", "P"),
            ("/html/body/form/input[31]", "E"),
            ("/html/body/form/input[32]", "B"),
            ("/html/body/form/input[33]", "F")
        ]
        
        for xpath, valor in campos:
            campo = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.execute_script("arguments[0].value = arguments[1]", campo, valor)
            time.sleep(1)
        
        
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/a[2]")))
        search_button.click()
        hour_click = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        
        time.sleep(2)
        attempts = int(os.getenv('ATTEMPTS'))
        
        for attempt in range(attempts):
            time.sleep(3)
            print(f"Tentativa {attempt + 1} de {attempts} para baixar o relatório 455.")
            
            downloaded = open_page_156(
                driver, 
                options="455", 
                date_time=hour_click
            )
            
            if downloaded:
                print("Relatório baixado com sucesso.")
                return downloaded

    except Exception as e:
        print(f"Erro ao processar o relatório 455: {e}")
        raise Exception(f"Falha no processo 455: {e}")
        
