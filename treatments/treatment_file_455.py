import pandas as pd
import numpy as np
from functions import ctrcs_list,searc_ctrcs_registers, merge_ctrcs, new_ctrcs, old_ctrcs, send_registers
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Robo-455")

def treat_file_455(new_file: str):
    
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
            'CEP de Entrega'
        ]
            ]
    
    df_tratado = df_tratado.replace({np.nan: None})

    response = searc_ctrcs_registers(
            ctrcs_list(df_tratado)
        )

    if response.status_code == 200:
        response_data = response.json()
        
        df_response = pd.DataFrame(response_data)
        
        df_registers = merge_ctrcs(
            df_tratado,
            df_response
        )
        
        df_new_registers = new_ctrcs(df_registers)
        df_old_registers = old_ctrcs(df_registers)
        
        logger.info(f"Enviando {len(df_new_registers)} novos registros")
        send_registers(df_new_registers, '455/', 'post')

        logger.info(f"Enviando {len(df_old_registers)} registros antigos")
        send_registers(df_old_registers, '455/', 'patch')
    else:
        print(response.status_code)
    
    # df_old_registers.to_excel('tratativa_455.xlsx', index=False)
