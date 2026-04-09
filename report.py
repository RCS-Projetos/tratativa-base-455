from ssw import SSW
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import concurrent.futures
import requests as rq
import os
import time
from ssw.selenium import Driver
from functions import ctrcs_list,searc_ctrcs_registers, merge_ctrcs, new_ctrcs, old_ctrcs, send_registers, make_report_log

class Report(SSW):
    def __init__(
        self, 
        driver: Driver,
        documents: str = 'new', 
        download_dir: str = 'Downloads',
        args: list[dict] = []
    ):
        super().__init__(driver, download_dir)
        self.documents = documents
        self.args = args
        self.file_path: str = ''
        self.payload:list = []
        self.logger.set_report('455')
    
    def build_args(self, args: list[dict], act:str='ENV', dummy: str = '1773317330121'):
        
        self.args.append({'key': 'act', 'value':act})
        self.args.append({'key': 'dummy', 'value':dummy})
        self.args.extend(args)
        
    def report(self, url:str):
        self.logger.start_report()
        args_str = ';\n        '.join([f'formData.append("{arg["key"]}", "{arg["value"]}")' for arg in self.args])
        
        script = f'''
        const url = arguments[0];
        const formData = new FormData();
        {args_str};
        
        fetch(url, {{
            method: 'POST',
            body: formData
        }}).then(() => {{
            console.log('success');
        }}).catch((error) => {{
            console.log(error);
        }});
        '''
        self.logger.info("Enviando relatório...")
        self.driver().driver().execute_script(script, url)
        sended_time = (datetime.now()-timedelta(seconds=15)).strftime("%d/%m/%y %H:%M:%S")
        self.logger.info("Relatório enviado com sucesso.")
        self.logger.info(f"Realizando Download")
        
        time.sleep(5)
        self.file_path = self.download_156('455', sended_time, '.csv')
    
    def process_report(self):
        try:
        
            df = pd.read_csv(
                self.file_path, 
                sep=';',
                header=1, 
                dtype=str, 
                encoding='latin-1'
            )
        
            mapa_colunas = {
                'Serie/Numero CTRC': 'Key',
                'PREFIXO': 'Prefix',
                'CTRC': 'CTRC',
                'DIGITO': 'Digit',
                'Chave CT-e': 'Access key',
                'Tipo do Documento': 'Document type',
                'Tipo de Baixa': 'Write off type',
                'Tipo do Frete': 'Freight type',
                'Unidade Emissora': 'Emitter unit',
                'Unidade Receptora': 'Receiving unit',
                'Placa de Coleta': 'Collection vehicle',
                'Cliente Remetente': 'Sender',
                'Cliente Destinatario': 'Recipient',
                'Cliente Pagador': 'Payer',
                'Cliente Expedidor': 'Dispatcher',
                'Cliente Recebedor': 'Receiver contact',
                'Valor da Mercadoria': 'Merchandise value',
                'Valor do Frete': 'Freight value',
                'Valor do ICMS': 'Icms value',
                'Valor do ISS': 'Iss value',
                'Peso Real em Kg': 'Real weight',
                'Peso Calculado em Kg': 'Calculated weight',
                'Cubagem em m3': 'Cubic volume',
                'Quantidade de Volumes': 'Volume quantity',
                'Quantidade de Pares': 'Pair quantity',
                'Login': 'Issuer user',
                'Praca Expedidora': 'Dispatch place',
                'Localizacao Atual': 'Current location description',
                'Previsao de Entrega': 'Delivery due',
                'Setor de Destino':'Delivery zone',
                'Chaves NF-es':'nfes'
            }

            df.rename(columns=mapa_colunas, inplace=True, errors='ignore')
            
            df[['Prefix', 'CTRC', 'Digit']] = df['Key'].str.extract(r'([A-Z]+)(\d+)-(\d+)')
            df['emission_date'] = pd.to_datetime(
                    df['Data de Emissao'].astype(str) + ' ' + df['Hora de Emissao'].astype(str),
                    dayfirst=True, # Importante para datas brasileiras (Dia/Mês/Ano)
                    errors='coerce'
                )
            df['authorization_date'] = pd.to_datetime(
                    df['Data de Autorizacao'].astype(str) + ' ' + df['Hora de Autorizacao'].astype(str),
                    dayfirst=True, # Importante para datas brasileiras (Dia/Mês/Ano)
                    errors='coerce'
                )

            df_tratado = \
                df[
                    [
                    # --- Itens Originais (Inglês) ---
                    'Key',
                    'Prefix',
                    'CTRC',
                    'Digit',
                    'Access key',
                    'Document type',
                    'Write off type',
                    'Freight type',
                    'Emitter unit',
                    'Receiving unit',
                    'Collection vehicle',
                    'Sender',
                    'Recipient',
                    'Payer',
                    'Dispatcher',
                    'Receiver contact',
                    'Merchandise value',
                    'Freight value',
                    'Icms value',
                    'Iss value',
                    'Real weight',
                    'Calculated weight',
                    'Cubic volume',
                    'Volume quantity',
                    'Pair quantity',
                    'Issuer user',
                    'Dispatch place',
                    'Current location description',
                    'Delivery due',
                    'emission_date',
                    'authorization_date',
                    'nfes',

                    # --- Itens Novos / Diferença (Português) ---
                    'CNPJ Remetente',
                    'Endereco do Remetente',
                    'Bairro do Remetente',
                    'Cidade do Remetente',
                    'UF do Remetente',
                    'CEP do Remetente',
                    'CNPJ Expedidor',
                    'Cidade do Expedidor',
                    'UF do Expedidor',
                    'CNPJ Pagador',
                    'Endereco do Pagador',
                    'Bairro do Pagador',
                    'Cidade do Pagador',
                    'UF do Pagador',
                    'CNPJ Destinatario',
                    'Endereco do Destinatario',
                    'Bairro do Destinatario',
                    'Cidade do Destinatario',
                    'UF do Destinatario',
                    'CEP do Destinatario',
                    'CNPJ Recebedor',
                    'Endereco',
                    'Bairro',
                    'Cidade de Entrega',
                    'UF de Entrega',
                    'CEP de Entrega',
                    'Delivery zone'
                ]
                    ]
            
            df_tratado = df_tratado.replace({np.nan: None})

            qtde_ctrcs = len(df_tratado)//6


            db_ctrcs_1 = df_tratado[:qtde_ctrcs]
            db_ctrcs_2 = df_tratado[qtde_ctrcs:qtde_ctrcs*2]
            db_ctrcs_3 = df_tratado[qtde_ctrcs*2:qtde_ctrcs*3]
            db_ctrcs_4 = df_tratado[qtde_ctrcs*3:qtde_ctrcs*4]
            db_ctrcs_5 = df_tratado[qtde_ctrcs*4:qtde_ctrcs*5]
            db_ctrcs_6 = df_tratado[qtde_ctrcs*5:]

            db_ctrcs = [db_ctrcs_1, db_ctrcs_2, db_ctrcs_3, db_ctrcs_4, db_ctrcs_5, db_ctrcs_6]

            response = []
            
            for i in db_ctrcs:
                print(f"Buscando {len(i)} de {len(df_tratado)} registros")
                response_api = searc_ctrcs_registers(
                    ctrcs_list(i)
                )

                if response_api.status_code == 200:
                    response_data = response_api.json()
                    print(F'Item encontrado')
                    response.extend(response_data)
                else:
                    print(F'Item não encontrado')
            

            if response:             
                df_response = pd.DataFrame(response)
                
                df_registers = merge_ctrcs(
                    df_tratado,
                    df_response
                )
                
                df_new_registers = new_ctrcs(df_registers)
                df_old_registers = old_ctrcs(df_registers)
                
                self.logger.info(f"Enviando {len(df_new_registers)} novos registros")
                send_registers(df_new_registers, '455/', 'post')

                self.logger.info(f"Enviando {len(df_old_registers)} registros antigos")
                send_registers(df_old_registers, '455/bulk-update/', 'patch')
                
                self.logger.info("Separando documentos")
                
                if self.documents == 'new':
                    df_documents = df_new_registers[['Key', 'nfes']].copy()
                else:
                    df_documents = df_registers[['Key', 'nfes']].copy()
                
                # Assegurar formato de lista para múltiplas chaves separadas por vírgula e explodir
                df_documents['nfes'] = df_documents['nfes'].astype(str).str.split(',')
                df_documents = df_documents.explode('nfes')
                df_documents['nfes'] = df_documents['nfes'].str.strip()
                
                # Filtrar apenas as chaves de tamanho válido (44 caracteres) para fatiar adequadamente
                df_documents = df_documents[df_documents['nfes'].str.len() == 44]
                
                # As posições [25:34] e [22:25] estão corretas para chaves NF-e de 44 dígitos
                df_documents['number'] = df_documents['nfes'].str[25:34]
                df_documents['serie'] = df_documents['nfes'].str[22:25]
                
                self.logger.info("Criando payload")
                payload = []
                for _, row in df_documents.iterrows():
                    payload.append({
                        'shipment_key': self.clean_text(row['Key']),
                        'number': self.clean_decimal(row['number']),
                        'serie': self.clean_decimal(row['serie']),
                        'key': self.clean_text(row['nfes'])
                    })
                
                BASE_URL = os.getenv('BASE_URL')
                
                try:
                    TIMEOUT = float(os.getenv('TIMEOUT')) if os.getenv('TIMEOUT') else None
                except ValueError:
                    TIMEOUT = None
                
                self.logger.info("Enviando documentos")
                
                BATCH_SIZE = 1000
                
                for i in range(0, len(payload), BATCH_SIZE):
                    self.logger.info(f"Enviando lote {i+BATCH_SIZE} de {len(payload)}")
                    if payload[i:i+BATCH_SIZE]:
                        response = rq.post(f'{BASE_URL}455/document/', json=payload[i:i+BATCH_SIZE], timeout=TIMEOUT)
                        if response.status_code in [200,201]:
                            self.logger.info(f"Lote {i+BATCH_SIZE} de {len(payload)} enviado com sucesso")
                        else:
                            self.logger.error(f"Erro ao enviar lote {i+BATCH_SIZE} de {len(payload)}")
                            self.logger.error(response.json())
                
            else:
                self.logger.info("Enviando todos os registros")
                send_registers(df_tratado, '455/', 'post')
                os.remove(self.file_path)
                return
                
            os.remove(self.file_path)
            
            self.logger.info("455 processado com sucesso")
            self.logger.finish_report()
            
        except Exception as e:
            self.logger.error(f"Erro ao processar o 455: {str(e)}")
            self.logger.error_report()
    
    def clean_decimal(self, value):
        if pd.isna(value) or str(value).strip() == '': return 0.0
        return float(str(value).strip().replace('.', '').replace(',', '.'))

    def clean_text(self, value):
        if pd.isna(value) or str(value).strip() == '': return None
        return str(value).strip()

    def clean_date(self, value, is_datetime=False):
        if pd.isna(value) or str(value).strip() == '': return None
        try:
            # Converte para datetime e depois para string ISO
            dt = pd.to_datetime(value, dayfirst=True)
            fmt = '%Y-%m-%dT%H:%M:%SZ' if is_datetime else '%Y-%m-%d'
            return dt.strftime(fmt)
        except:
            return None