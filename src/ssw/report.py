import logging
from abc import ABC, abstractmethod
from typing import final
from .ssw import SSWService
from src.websocket import Driver
from datetime import datetime, timedelta

class Report(SSWService, ABC):
    def __init__(self,driver:Driver, report_name: str, url:str='', payload: list=[], send_button: str='', is_156: bool = True):
        super().__init__(driver=driver)
        self.__report_name = report_name
        self.__url = url
        self.__payload = payload
        self.__send_button = send_button
        self.__logger = logging.getLogger(f'Relatorio: {self.__report_name}')
        self.__is_156 = is_156
    
    @property
    def report_name(self) -> str:
        return self.__report_name
    
    @final
    def run(self):
        try:
            
            resp_login = self.login()
            
            if resp_login['status'] == 'error':
                self.__logger.error(f"Erro ao fazer login: {resp_login['message']}")
                return resp_login
            
            return self.execute_logic()
        
        except Exception as e:
            self.__logger.error(f"Erro ao executar lógica: {e}")
            return {'status': 'error', 'message': f'Erro ao executar lógica: {e}'}

        finally:
            self.driver.quit()
    

    def execute_logic(self):
        self.__logger.info(f"Executando lógica para o relatório {self.__report_name}")
        self.default_report()
    
    @final
    def default_report(self):
        self._driver.get(self.__url)
        self.send_keys(self.__payload)
        self.click(self.__send_button)
        if self.__is_156:
            data, download_resp = self.download_line((datetime.now()-timedelta(seconds=5)).strftime("%d/%m/%y %H:%M:%S"), self.__report_name)
            if download_resp['status'] == 'success':
                return data
            return None
        else:
            self.download()
        
    @property
    def driver(self):
        return self._driver
        