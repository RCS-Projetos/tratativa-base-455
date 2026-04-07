import logging
import requests
import os
from dotenv import load_dotenv
from typing import Literal, Optional

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Logger:
    def __init__(self):
        self.logger = logger
        self.url = os.getenv('BASE_URL')
        self.report = ""
        self.report_id = None
    
    def set_report(self, report: str):
        self.report = report
    
    def headers(self) -> dict:
        return {
            "Content-Type": "application/json"
        }
    
    def data(self, message: Literal['STARTED', 'FINISHED', 'ERROR']) -> dict:
        return {
            "report_type": self.report,
            "status": message
        }
    
    def start_report(self):
        data = self.data('STARTED')
        response = requests.post(f'{self.url}report-log/', json=data, headers=self.headers())
        self.report_id = response.json()['id']
    
    def finish_report(self):
        data = self.data('FINISHED')
        response = requests.patch(f'{self.url}report-log/{self.report_id}/', json=data, headers=self.headers())
        self.report_id = response.json()['id']
    
    def error_report(self):
        data = self.data('ERROR')
        response = requests.patch(f'{self.url}report-log/{self.report_id}/', json=data, headers=self.headers())
        self.report_id = response.json()['id']
        
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    
