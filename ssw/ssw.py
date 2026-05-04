import os
import time
import random
from dotenv import load_dotenv
from .functions import Login
from .selenium import Driver
from .functions.logger import Logger
from .functions import Download, ReportDownloader

load_dotenv()


class SSW:
    def __init__(self, driver: Driver, download_dir: str = 'Downloads'):
        self.logger = Logger()
        self.company = os.getenv("SSW_COMPANY")
        users = os.getenv("SSW_USER", "").split(',')
        passwords = os.getenv("SSW_PASSWORD", "").split(',')
        taxes = os.getenv("SSW_TAX", "").split(',')
        used_user = ''
        
        self.credentials = []
        for u, p, t in zip(users, passwords, taxes):
            self.credentials.append({
                'user': u.strip(),
                'password': p.strip(),
                'tax': t.strip()
            })
        
        self.batch_size = int(os.getenv("BATCH_SIZE", "100"))
        self.attemps = int(os.getenv("ATTEMPTS", "3"))
        self.download_dir = download_dir
        self.driver_instance = driver
    
    def driver(self):
        return self.driver_instance

    def make_login(self):
        url = 'https://sistema.ssw.inf.br/bin/ssw0422'
        self.logger.info("Realizando login")
        
        # Seleciona uma credencial aleatória
        cred = random.choice(self.credentials)
        self.logger.info(f"Usando usuário: {cred['user']}")
        self.used_user = cred['user']
        
        login = Login(self.driver_instance, self.company, cred['tax'], cred['user'], cred['password'], url)
        login.login()
        time.sleep(1)
        self.logger.info("Login realizado")

    def close(self):
        time.sleep(10)
        self.driver_instance.quit()

    def report(self):
        #Altere o Report AQUI
        ...
        
    def get_index(self, report:str, sended_time: str):
        
        for attempt in range(self.attemps):
            time.sleep(3)
            report_downloader = ReportDownloader(self.driver_instance, report, self.used_user, sended_time)
            index = report_downloader.ssw_156()
            if index:
                return index
        return False

    def download_156(self, report: str, sended_time: str, default_extension: str = '.csv'):
        index = self.get_index(report, sended_time)
        if not index:
            return False

        download = Download(self.driver_instance, index, default_extension)
        file = download.download()
        return file

    def execute_report(self, **kwargs):
        self.make_login()
        time.sleep(3)
        self.report(**kwargs)
        self.close()
