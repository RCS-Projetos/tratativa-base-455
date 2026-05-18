import os
from .logger import Logger

class Files:
    def __init__(self, download_dir: str = 'Downloads', default_extension: str = '.csv'):
        self.logger = Logger()
        self.download_dir = download_dir
        self.default_extension = default_extension
        
        # CORREÇÃO 1: Garante que a pasta exista assim que a classe for instanciada.
        # Se a pasta já existir, o exist_ok=True faz ele seguir a vida normalmente.
        os.makedirs(self.get_download_path(), exist_ok=True)
    
    def get_download_path(self):
        return os.path.join(os.path.expanduser("~"), self.download_dir)
    
    def get_downloaded_file(self):
        # Retorna um SET com os caminhos dos arquivos encontrados
        return set([os.path.join(self.get_download_path(), f) for f in os.listdir(self.get_download_path()) if f.endswith(self.default_extension)])
    
    def rename_download_file(self, new_name: str):
        # CORREÇÃO 2: 
        # a) O nome do método acima é get_downloaded_file (com 'ed' no final).
        # b) Como ele retorna um SET, não podemos passar direto pro os.rename. 
        # Precisamos pegar o primeiro arquivo da lista.
        arquivos = self.get_downloaded_file()
        if arquivos:
            arquivo_atual = list(arquivos)[0] # Pega o primeiro arquivo encontrado
            os.rename(arquivo_atual, new_name)
        else:
            self.logger.warning("Nenhum arquivo encontrado para renomear.")
    
    def delete_download_file(self):
        # Mesma correção aplicada ao delete
        arquivos = self.get_downloaded_file()
        if arquivos:
            arquivo_atual = list(arquivos)[0]
            os.remove(arquivo_atual)
        else:
            self.logger.warning("Nenhum arquivo encontrado para deletar.")