import os


def validar_arquivos_pasta(downloads_path, default_extension: str = '.csv'):
    files = set([os.path.join(downloads_path, f) for f in os.listdir(downloads_path) if f.endswith(default_extension)])
    return files