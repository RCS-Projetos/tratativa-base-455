import os
import time
from dotenv import load_dotenv
from .functions import Login
from .selenium import Driver
from .functions.logger import Logger
from .functions import Download, ReportDownloader

load_dotenv()


class SSW:
    def __init__(self, driver: Driver, download_dir: str = 'Downloads'):
        self.logger = Logger()
        self.tax = os.getenv("SSW_TAX")
        self.company = os.getenv("SSW_COMPANY")
        self.user = os.getenv("SSW_USER")
        self.password = os.getenv("SSW_PASSWORD")
        self.batch_size = int(os.getenv("BATCH_SIZE"))
        self.attemps = int(os.getenv("ATTEMPTS"))
        self.download_dir = download_dir
        self.driver_instance = driver
    
    def driver(self):
        return self.driver_instance

    def make_login(self):
        url = 'https://sistema.ssw.inf.br/bin/ssw0422'
        self.logger.info("Realizando login")
        login = Login(self.driver_instance, self.company, self.tax, self.user, self.password, url)
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
            report_downloader = ReportDownloader(self.driver_instance, report, sended_time)
            index = report_downloader.ssw_156()
            if index:
                return index
        return False

    def download_156(self, report: str, sended_time: str, default_extension: str = '.sswweb'):
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
