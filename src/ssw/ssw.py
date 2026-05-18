import logging
import random
import pandas as pd
import os
from io import StringIO
from typing import final
from dotenv import load_dotenv
load_dotenv()
import time

class SSWService:
    def __init__(self, driver):
        self._driver = driver
        self.__logger = logging.getLogger('ssw.services')
        self.__logger.info('SSW Service initialized')
        
        profile_res = self.get_user_profile()
        if profile_res['status'] == 'success':
            self.__user = profile_res['data']
        else:
            raise Exception("Não foi possível carregar credenciais")
        
    @final
    def login(self):
        self.__logger.info(f"Login no SSW com usuário {self.__user['user']}")
        
        try:
            try:
                self._driver.get('https://sistema.ssw.inf.br/bin/ssw0422')
            except Exception as e:
                self.__logger.error(f"Erro ao acessar página de login: {e}")
                return {'status': 'error', 'message': 'Erro ao acessar página de login'}
            
            try:
                path = lambda x : f"xpath=/html/body/form/input[{x}]"
                xpaths = {
                    'company': path(1),
                    'tax':path(2),
                    'user': path(3),
                    'password': path(4),
                }

                list_keys = [(xpaths[key], self.__user[key]) for key in self.__user.keys()]
                
                for xpath, value in list_keys:
                    element = self._driver.page.locator(xpath)
                    element.evaluate("(el, val) => el.value = val", value)
                
                try:
                    self._driver.page.locator('xpath=/html/body/form/a').click()
                except Exception as e:
                    self.__logger.error(f"Erro ao clicar no botão de login: {e}")
                    return {'status': 'error', 'message': 'Erro ao clicar no botão de login'}
                
            except Exception as e:
                self.__logger.error(f"Erro ao preencher campos de login: {e}")
                return {'status': 'error', 'message': 'Erro ao preencher campos de login'}
            
            try:
                self.__logger.info('Verificando Login')
                self._driver.page.wait_for_url('https://sistema.ssw.inf.br/bin/menu01')
                self.__logger.info('Login realizado com sucesso')
                return {'status': 'success', 'message': 'Login realizado com sucesso'}
            except Exception as e:
                self.__logger.error(f"Erro ao verificar login: {e}")
                return {'status': 'error', 'message': 'Erro ao verificar login'}

        except Exception as e:
            self.__logger.error(f"Erro ao fazer login no SSW: {e}")
            return {'status': 'error', 'message': 'Erro ao fazer login no SSW'}

    @final
    def download(self, default_ext: str = '.csv'):
        pass
    
    
    @final
    def send_keys(self, payload: list[dict]):
        page = self._driver.page
        for f in payload:
            try:
                element = page.locator(f['xpath'])
                element.evaluate("(el, val) => el.value = val", f['value'])
            except Exception as e:
                self.__logger.error(f"Erro ao preencher campo {f['field']}: {e}")
                return {'status': 'error', 'message': f'Erro ao preencher campo {f['field']}: {e}'}
    
        self.__logger.info('Campos preenchidos com sucesso')
        return {'status': 'success', 'message': 'Campos preenchidos com sucesso'}
    
    @final
    def click(self, xpath: str):
        page = self._driver.page
        try:
            element = page.locator(xpath)
            element.click()
        except Exception as e:
            self.__logger.error(f"Erro ao clicar no botão {xpath}: {e}")
            return {'status': 'error', 'message': f'Erro ao clicar no botão {xpath}: {e}'}
        
        self.__logger.info('Botão clicado com sucesso')
        return {'status': 'success', 'message': 'Botão clicado com sucesso'}
    
    @final
    def download_line(self, date_time_click:str, report_name:str):
        
        downloaded = False
        count = 1
        while downloaded == False:
            time_to_sleep = random.randint(3, 5)
            time.sleep(time_to_sleep)
            try:
                self._driver.get('https://sistema.ssw.inf.br/bin/ssw1440')
                self._driver.page.wait_for_load_state('domcontentloaded')
                self.__logger.info(f'Tentativa Nº{count}')
                count+=1
                download_response = self.download_table_validator(date_time_click, report_name)
                
                if download_response['status'] == 'success':
                    downloaded = True
                    return download_response['data'], {'status': 'success', 'message': 'Download realizado com sucesso'}
                
                if count >= 30:
                    return None, {'status': 'error', 'message': 'Erro ao baixar arquivo'}
            except Exception as e:
                self.__logger.error(f"Erro ao baixar arquivo: {e}")
                return None, {'status': 'error', 'message': f'Erro ao baixar arquivo: {e}'}

    @final
    def download_table(self):
        xpath_table = 'xpath=/html/body/form/div[2]/div[2]/table[1]'
        try:
            self._driver.page.wait_for_selector(xpath_table, state='visible', timeout=10000)
            
            table_page = self._driver.page.locator(xpath_table).evaluate("el => el.outerHTML")
            
            if not table_page:
                self.__logger.error("Tabela encontrada, mas o conteúdo HTML está vazio.")
                return pd.DataFrame()

            df = pd.read_html(StringIO(table_page), header=0)[0]
            
            if 'Opção' in df.columns:
                df['Opção'] = df['Opção'].astype(str).str[0:3]
                
            return df

        except Exception as e:
            self.__logger.error(f"Erro ao processar tabela HTML: {e}")
            return pd.DataFrame()
    
    @final
    def download_table_validator(self, date_time_click:str, report_name:str):
        df = self.download_table()
        table_date_time = pd.to_datetime(date_time_click)
        mask = (
            (df['Opção'] == report_name) & 
            (df['Usuário'] == self.__user['user']) & 
            (df['Data/Hora Solicitação'].astype('datetime64[ns]') >= table_date_time) &
            (df['Unnamed: 8'] == 'Baixar')
        )

        df['validated'] =  mask
        validated_index = df[mask].index.tolist()
        if len(validated_index)>0:
            with self._driver.page.expect_download() as download_info:
                self.download_button(validated_index[0]+2)
                
                download = download_info.value
               
                if download:
                    download_path = f'{self._driver._download_dir}\{download_info.value.suggested_filename}'
                    download.save_as(download_path)
                    self.__logger.info(f'Download realizado com sucesso {download_path}')
                    return {'status': 'success', 'message': 'Download realizado com sucesso', 'data': download_path}
                else:
                    return {'status': 'error', 'message': 'Nenhum arquivo encontrado', 'data': None}
        else:
            return {'status': 'error', 'message': 'Botão não disponivel', 'data': None}
        
    @final
    def download_button(self, index: int):
        button = self._driver.page.locator(f'xpath=/html/body/form/div[2]/div[2]/table[1]/tbody/tr[{index}]/td[9]/div/a')
        button.click()
    
    @final
    def get_user_profile(self):
        try:
            users = os.getenv("SSW_USER", "").split(',')
            passwords = os.getenv("SSW_PASSWORD", "").split(',')
            taxes = os.getenv("SSW_TAX", "").split(',')
            
            credentials = [{
                'company': 'RCS',
                'user': u.strip(),
                'password': p.strip(),
                'tax': t.strip()
            } for u, p, t in zip(users, passwords, taxes)]
        
            user = random.choice(credentials)
            return {'status': 'success', 'message': 'Credenciais obtidas com sucesso', 'data': user}
        except Exception as e:
            self.__logger.error(f"Erro ao obter credenciais: {e}")
            return {'status': 'error', 'message': f'Erro ao obter credenciais: {e}'}