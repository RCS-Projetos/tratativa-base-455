import pandas as pd
import requests as rq
import os
import concurrent.futures
from .logger import Logger

class Tools:
    def __init__(self, base_url: str = None):
        self.logger = Logger()
        if base_url is None:
            self.base_url = os.getenv('BASE_URL')
        else:
            self.base_url = base_url

    def read_csv(self, file_path: str, sep: str = ';', header:int =0, dtype:str = str, encoding:str = 'latin-1'):
        return pd.read_csv(file_path, sep=sep, header=header, dtype=dtype, encoding=encoding)
    
    def read_excel(self, file_path: str, header=0):
        return pd.read_excel(file_path, header=header)
    
    def read_json(self, file_path: str):
        return pd.read_json(file_path)
    
    def rename(self, columns:dict, inplace:bool = True, errors:str = 'ignore'):
        return self.rename(columns=columns, inplace=inplace, errors=errors)

    def normalize_date(self, series: pd.Series):
        dates = pd.to_datetime(series, utc=True, errors='coerce')
        dates = dates.dt.tz_localize(None)
        return dates.dt.strftime('%Y-%m-%d %H:%M:%S').fillna('')

    def clean_date(self, value, is_datetime:bool=False):
        if isinstance(value, pd.Series):
            value = value.iloc[0] if not value.empty else None

        if pd.isna(value) or str(value).strip() == '': return None
        try:
            date = pd.to_datetime(value, dayfirst=False, errors='coerce')
            fmt = '%Y-%m-%dT%H:%M:%SZ' if is_datetime else '%Y-%m-%d'
            return date.strftime(fmt)
        except:
            return None

    def clean_text(self, value):
        if isinstance(value, pd.Series):
            value = value.iloc[0] if not value.empty else None
        if pd.isna(value) or str(value).strip() == '': return None
        return str(value).strip()
    
    def clean_decimal(self, value):
        if isinstance(value, pd.Series):
            value = value.iloc[0] if not value.empty else None
        if pd.isna(value) or str(value).strip() == '': return 0.0
        return float(str(value).strip().replace('.', '').replace(',', '.'))

    def select_columns(self, table: pd.DataFrame, columns: list[str]):
        return table[columns]
    

    def ctrcs_keys_to_list(self, table: pd.DataFrame):
        return table['key'].tolist()


    def sep_list(self, list_or_dataframe: list | pd.DataFrame, qtde_items: int = 6):

       batch_size = len(list_or_dataframe)/qtde_items
       
       list_result = []
       for i in range(0, qtde_items):
           mult = i + 1
           list_result.append(list_or_dataframe[int(batch_size*i):int(mult*batch_size)])
       return list_result

    def request(self, timeout:int = 30, headers: dict = None):
        if headers is None: headers = {}
        header = {
            **headers,
            "Content-Type": "application/json",
        }
        
        class RequestHandler:
            def post(self, url_api:str, json:dict = None, data:dict = None):
                payload = json if json is not None else data
                return rq.post(url_api, headers=header, timeout=timeout, json=payload)
            
            def get(self, url_api:str):
                return rq.get(url_api, headers=header, timeout=timeout)
            
            def patch(self, url_api:str, json:dict = None, data:dict = None):
                payload = json if json is not None else data
                return rq.patch(url_api, headers=header, timeout=timeout, json=payload)
            
            def put(self, url_api:str, json:dict = None, data:dict = None):
                payload = json if json is not None else data
                return rq.put(url_api, headers=header, timeout=timeout, json=payload)
            
            def delete(self, url_api:str):
                return rq.delete(url_api, headers=header, timeout=timeout)

        return RequestHandler()
    
    def merge(self, table_one: pd.DataFrame, table_two: pd.DataFrame, left_on: str = 'key', right_on: str = 'key',how: str = 'left'):
        return pd.merge(table_one, table_two, left_on=left_on, right_on=right_on, how=how)

    def batch_request(self, table: pd.DataFrame, url_api: str, method: str = 'post', qtde_items: int = 6):
        payload_list = [self.build_payload(row) for _, row in table.iterrows()]

        if method == 'post':
            response = self.request().post(url_api, json=payload_list)
        elif method == 'patch':
            response = self.request().patch(url_api, json=payload_list)
        else:
            self.logger.error(f'Método não suportado: {method}')
            raise Exception(f'Método não suportado: {method}')
        
        if response.status_code in [200, 201]:
            self.logger.info(f'Requisição realizada com sucesso: {response.status_code}')
            return response.json()
        else:
            self.logger.error(f'Erro ao enviar requisição para a API: {response.status_code}')
            print(payload_list)
            raise Exception(f'Erro ao enviar requisição para a API: {response.status_code}')

    
        
        
        
