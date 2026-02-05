import pandas as pd
import numpy as np
from functions import ctrcs_list,searc_ctrcs_registers, merge_ctrcs, new_ctrcs, old_ctrcs, send_registers, make_report_log
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Robo-455")

def treat_file_455(new_file: str, report_log_id: int):
    try:
        
        df = pd.read_csv(
            new_file, 
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
            'Entrega Programada': 'Delivery date',
            'Setor de Destino':'Delivery zone'
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
                'Delivery date',
                'emission_date',
                'authorization_date',

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
            
            logger.info(f"Enviando {len(df_new_registers)} novos registros")
            send_registers(df_new_registers, '455/', 'post')

            logger.info(f"Enviando {len(df_old_registers)} registros antigos")
            send_registers(df_old_registers, '455/bulk-update/', 'patch')

        else:
            logger.info("Enviando todos os registros")
            send_registers(df_tratado, '455/', 'post')
            os.remove(new_file)
            make_report_log('455', 'FINISHED', 'patch', report_log_id)
            return
            
        os.remove(new_file)
        
        logger.info("455 processado com sucesso")
        make_report_log('455', 'FINISHED', 'patch', report_log_id)
        
    except Exception as e:
        make_report_log('455', 'ERROR', 'patch', report_log_id)
        logger.error(f"Erro ao processar o 455: {str(e)}")