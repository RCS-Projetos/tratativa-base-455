import os
import requests as rq
import pandas as pd
from pandas import DataFrame
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv('BASE_URL')

BATCH_SIZE = int(os.getenv('BATCH_SIZE'))
TIMEOUT = int(os.getenv('TIMEOUT'))

url_path = lambda x: f'{BASE_URL}{x}'

headers = {
    "Content-Type": "application/json" # Remova se não usar auth
}

def searc_ctrcs_registers(ctrcs: list[str]) -> rq.Response:
    
    url = url_path('455/get-by-keys/')
    
    response = rq.post(
        url,
        json={             
            'keys': ctrcs
        },
        timeout=TIMEOUT
    )
  
    return response

def ctrcs_list(df: DataFrame)-> list[str]:
    return df['Key'].to_list()

def merge_ctrcs(df_file: DataFrame, df_response: DataFrame) -> DataFrame:
    df = df_file.merge(
            df_response,
            left_on='Key',
            right_on='key',
            how='left'
        )
    
    return df
        
def new_ctrcs(df: DataFrame) -> DataFrame:
    df_new_registers = df[(df['id'].isna()) & (df['Prefix'].notna())].copy()
    return df_new_registers

def old_ctrcs(df: DataFrame) -> DataFrame:
    df_registered = df[df['id'].notna()].copy()
    
    # Função auxiliar para extrair texto de dicionários se necessário
    def extract_text(val):
        if isinstance(val, dict):
            return str(val.get('name') or val.get('description') or val.get('code') or '')
        return str(val) if pd.notna(val) else ''

    # Normalização de strings para comparação robusta
    def normalize(series):
        # Primeiro extrai texto de objetos/dicts se houver, converte tudo para string
        s = series.apply(extract_text)
        # Remove .0 de floats, espaços extras e converte para minúsculo
        return s.str.replace(r'\.0$', '', regex=True).str.strip().str.lower()
    
    # Normalização de datas para YYYY-MM-DD
    def normalize_date(series):
        # 1. Tenta ler no formato exato do banco de dados (YYYY-MM-DD)
        s_banco = pd.to_datetime(series, format='%Y-%m-%d', errors='coerce')
        
        # 2. Tenta ler no formato da planilha (DD/MM/YYYY) com dayfirst=True
        s_planilha = pd.to_datetime(series, dayfirst=True, errors='coerce')
        
        # 3. Combina os dois: se falhou no formato do banco (ficou NaT), usa o da planilha
        s_final = s_banco.fillna(s_planilha)
        
        # 4. Converte tudo para string padronizada
        return s_final.dt.strftime('%Y-%m-%d').fillna('')

    mask = (
        (normalize(df_registered['Current location description']) != normalize(df_registered['current_location'])) | 
        (normalize(df_registered['Delivery zone']) != normalize(df_registered['delivery_zone'])) | 
        (normalize(df_registered['Write off type']) != normalize(df_registered['write_off_type'])) | 
        (normalize_date(df_registered['Delivery due']) != normalize_date(df_registered['delivery_due'])) |
        (normalize(df_registered['Receiving unit']) != normalize(df_registered['receiving_unit']))
    )
    
    df_registered_to_update = df_registered[mask]
    return df_registered_to_update


def clean_decimal(value):
    if pd.isna(value) or str(value).strip() == '': return 0.0
    return float(str(value).strip().replace('.', '').replace(',', '.'))

def clean_text(value):
    if pd.isna(value) or str(value).strip() == '': return None
    return str(value).strip()

def clean_date(value, is_datetime=False):
    if pd.isna(value) or str(value).strip() == '': return None
    try:
        # Converte para datetime e depois para string ISO
        dt = pd.to_datetime(value, dayfirst=True)
        fmt = '%Y-%m-%dT%H:%M:%SZ' if is_datetime else '%Y-%m-%d'
        return dt.strftime(fmt)
    except:
        return None

     
def build_payload(row):
        # Helper para criar cliente aninhado
        def build_customer(role_name, cnpj_col, name_col, addr_col, neigh_col, city_col, uf_col, cep_col):
            name = clean_text(row.get(name_col))
            if not name: return None
            
            customer = {
                "name": name,
                "tax_id": clean_text(row.get(cnpj_col))
            }
            
            # Endereço
            city_name = clean_text(row.get(city_col))
            if city_name:
                address = {
                    "street": clean_text(row.get(addr_col)) if row.get(addr_col) else "nao-encontrado",
                    "neighborhood": clean_text(row.get(neigh_col)),
                    "zip_code": clean_text(row.get(cep_col)),
                    "city": {
                        "name": city_name,
                        "state": {"abbreviation": clean_text(row.get(uf_col))}
                    }
                }
                customer['address'] = address
            return customer

        # Objeto Principal (Shipment)
        record = {
            "key": row.get('Key'),
            "prefix": clean_text(row.get('Prefix')),
            "ctrc": clean_text(row.get('CTRC')),
            "digit": clean_text(row.get('Digit')),
            "access_key": clean_text(row.get('Access key')),
            "current_location_description": clean_text(row.get('Current location description')),
            "delivery_zone": clean_text(row.get('Delivery zone')),
            
            # Valores Numéricos
            "merchandise_value": clean_decimal(row.get('Merchandise value')),
            "freight_value": clean_decimal(row.get('Freight value')),
            "real_weight": clean_decimal(row.get('Real weight')),
            "cubic_volume": clean_decimal(row.get('Cubic volume')),
            "calculated_weight": clean_decimal(row.get('Calculated weight')),
            "volume_quantity": int(clean_decimal(row.get('Volume quantity'))),
            
            # Datas ISO
            "delivery_due": clean_date(row.get('Delivery due')),
            "emission_date": clean_date(row.get('emission_date'), is_datetime=True),
            "authorization_date": clean_date(row.get('authorization_date'), is_datetime=True),
            
            # Foreign Keys (Lookups)
            "document_type": {"name": clean_text(row.get('Document type'))} if row.get('Document type') else None,
            "write_off_type": {"name": clean_text(row.get('Write off type'))} if row.get('Write off type') else None,
            "freight_type": {"name": clean_text(row.get('Freight type'))} if row.get('Freight type') else None,
            "emitter_unit": {"code": clean_text(row.get('Emitter unit'))} if row.get('Emitter unit') else None,
            "receiving_unit": {"code": clean_text(row.get('Receiving unit'))} if row.get('Receiving unit') else None,
            "collection_vehicle": {"name": clean_text(row.get('Collection vehicle'))} if row.get('Collection vehicle') else None,

            # Foreign Keys (Customers Aninhados)
            "sender": build_customer("sender", "CNPJ Remetente", "Sender", "Endereco do Remetente", "Bairro do Remetente", "Cidade do Remetente", "UF do Remetente", "CEP do Remetente"),
            "recipient": build_customer("recipient", "CNPJ Destinatario", "Recipient", "Endereco do Destinatario", "Bairro do Destinatario", "Cidade do Destinatario", "UF do Destinatario", "CEP do Destinatario"),
            "payer": build_customer("payer", "CNPJ Pagador", "Payer", "Endereco do Pagador", "Bairro do Pagador", "Cidade do Pagador", "UF do Pagador", None),
            "dispatcher": build_customer("dispatcher", "CNPJ Expedidor", "Dispatcher", "Endereco do Remetente", "Bairro do Remetente", "Cidade do Expedidor", "UF do Expedidor", None)
        }
        
        # Remove chaves com valor None para limpar o payload
        record = {k: v for k, v in record.items() if v is not None}
        return record
    

def send_registers(df: pd.DataFrame, url: str, method: str):
    total_rows = len(df)
    print(f"Iniciando envio de {total_rows} registros...")
    
    for start_idx in range(0, total_rows, BATCH_SIZE):
        end_idx = start_idx + BATCH_SIZE
        batch_df = df.iloc[start_idx:end_idx]
        
        # Converte as linhas do lote atual para a lista de JSONs
        payload_list = [build_payload(row) for _, row in batch_df.iterrows()]
        
        try:
            # Envia o POST
            if method == 'post':
                response = rq.post(url_path(url), json=payload_list, headers=headers)
            elif method == 'patch':
                print(payload_list[0:3])
                response = rq.patch(url_path(url), json=payload_list, headers=headers)
            else:
                raise 'Nenhum metodo selecionado.' 
            
            # Verifica sucesso
            if response.status_code in [200, 201]:
                print(f"Lote {start_idx}-{end_idx} enviado com sucesso. {"Atualizado"}")
            else:
                print(f"Erro no lote {start_idx}-{end_idx}: {response.status_code}")
                print(f"Erro no lote {start_idx}-{end_idx}: {response.status_code}")
                with open('error.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("Resposta de erro salva em 'error.html'")
        except Exception as e:
            print(f"Exceção crítica no lote {start_idx}-{end_idx}: {str(e)}") 

data = {
    "Key": "AXA045062-6",
    "Access key": "31260219451038004449570010000444161015380924 ",
    "Delivery zone": "05  SUMARE",
    "Receiving unit": "CPQ",
    "Write off type": "FATURADO",
    "Delivery due": "05/03/2026",
    "Current location description": "CTRC ENTREGUE/BAIXADO",
    "id": 871201,
    "key": "AXA045062-6",
    "current_location": "CTRC ENTREGUE/BAIXADO",
    "access_key": "31260219451038004449570010000444161015380924",
    "delivery_zone": "05  SUMARE",
    "delivery_due": "2026-03-05",
    "write_off_type": "faturado",
    "receiving_unit": "CPQ"
}

df = pd.DataFrame([data])
print(df)

df = old_ctrcs(df)
print(df)
