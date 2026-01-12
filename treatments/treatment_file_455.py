import pandas as pd

def treat_file_455(new_file: str):
    print(new_file)
    df = pd.read_csv(new_file, sep=';',header=1, dtype=str, encoding='latin-1')

    df[['PREFIXO', 'CTRC', 'DIGITO']] = df['Serie/Numero CTRC'].str.extract(r'([A-Z]+)(\d+)-(\d+)')
    df['DATA_HORA_EMISSAO'] = pd.to_datetime(
            df['Data de Emissao'].astype(str) + ' ' + df['Hora de Emissao'].astype(str),
            dayfirst=True, # Importante para datas brasileiras (Dia/Mês/Ano)
            errors='coerce'
        )
    df['DATA_HORA_AUTORIZACAO'] = pd.to_datetime(
            df['Data de Autorizacao'].astype(str) + ' ' + df['Hora de Autorizacao'].astype(str),
            dayfirst=True, # Importante para datas brasileiras (Dia/Mês/Ano)
            errors='coerce'
        )

    df_tratado = \
        df[
            [
                'PREFIXO', 
                'CTRC', 
                'DIGITO', 
                'Tipo do Documento', 
                'Praca Expedidora', 
                'Unidade Emissora', 
                'Unidade Receptora', 
                'Login', 
                'Placa de Coleta', 
                'Chave CT-e', 
                'Valor da Mercadoria', 
                'Valor do Frete', 
                'Valor do ICMS', 
                'Valor do ISS', 
                'Peso Real em Kg', 
                'Cubagem em m3', 
                'Peso Calculado em Kg', 
                'Quantidade de Volumes', 
                'Quantidade de Pares', 
                'Tipo do Frete', 
                'Tipo de Baixa',
                'Localizacao Atual',
                'CNPJ Remetente', 
                'Cliente Remetente', 
                'Endereco do Remetente', 
                'Bairro do Remetente', 
                'Cidade do Remetente', 
                'UF do Remetente', 
                'CEP do Remetente', 
                'CNPJ Expedidor', 
                'Cliente Expedidor', 
                'Cidade do Expedidor', 
                'UF do Expedidor', 
                'CNPJ Pagador', 
                'Cliente Pagador',
                'Endereco do Pagador',
                'Bairro do Pagador',
                'Cidade do Pagador', 
                'UF do Pagador',
                'CNPJ Destinatario', 
                'CNPJ Destinatario', 
                'Cliente Destinatario', 
                'Endereco do Destinatario', 
                'Bairro do Destinatario', 
                'Cidade do Destinatario', 
                'UF do Destinatario',
                'CEP do Destinatario', 
                'CNPJ Recebedor', 
                'Cliente Recebedor', 
                'Endereco', 
                'Bairro', 
                'Cidade de Entrega', 
                'UF de Entrega', 
                'CEP de Entrega',
                'DATA_HORA_EMISSAO', 
                'DATA_HORA_AUTORIZACAO'
                ]
            ]
        
    df_tratado.to_excel("tratativa_455.xlsx", index=False)