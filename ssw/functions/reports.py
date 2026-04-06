import pandas as pd
from io import StringIO
from pandas import DataFrame
from datetime import datetime
from ..selenium import Driver
from .logger import Logger
import os

class ReportDownloader:
    def __init__(self, driver: Driver, report:str, date_time: datetime, url: str = 'https://sistema.ssw.inf.br/bin/ssw1440'):
        self.logger = Logger()
        self.driver = driver
        self.url = url
        self.report = report
        self.date_time = date_time
        self.user = os.getenv("SSW_USER")
    
    def report_table(self, table_html: str) -> pd.DataFrame:
        table = pd.read_html(StringIO(table_html), header=0)[0]
        table['Opção'] = table['Opção'].str[0:3]
        return table
    
    def get_report_table(self) -> pd.DataFrame:
        table_html = self.driver.wait_until('/html/body/form/div[2]/div[2]/table[1]').get_attribute('outerHTML')
        return self.report_table(table_html)

    def validate_report(self, table: pd.DataFrame) -> int | None:
        table_copy = table.copy()
        table_date_time = pd.to_datetime(self.date_time)
        mask = (
            (table_copy['Opção'] == self.report) & 
            (table_copy['Usuário'] == self.user) & 
            (table_copy['Data/Hora Solicitação'].astype('datetime64[ns]') >= table_date_time) &
            (table_copy['Unnamed: 8'] == 'Baixar')
        )

        table_copy['validated'] =  mask
        
        validated_index = table_copy[mask].index.tolist()
        return validated_index[0]+2 if len(validated_index)>0 else None

    def ssw_156(self):
        webdriver = self.driver.driver()
        
        if webdriver.current_url != self.url:
            self.driver.get(self.url)
        else:
            webdriver.refresh()
        
        index = self.validate_report(self.get_report_table())

        return index if index else None
        
        
    
    



    
