import os
import time
from . import Files
from .logger import Logger


class Download:
    def __init__(self, driver, index: int, default_extension: str = '.csv', download_dir: str = 'Downloads', timeout: int = 60):
        self.logger = Logger()
        self.driver = driver
        self.index = index
        self.download_button = f'/html/body/form/div[2]/div[2]/table[1]/tbody/tr[{self.index}]/td[9]/div/a'
        self.default_extension = default_extension
        self.download_dir = download_dir
        self.timeout = timeout

    def files(self):
        return Files(self.download_dir, self.default_extension)
    
    def press_download(self):
        download_button = self.driver.wait_until(self.download_button)
        self.driver.driver().execute_script("arguments[0].click();", download_button)
    

    def download(self):
        self.logger.info("Iniciando download")
        downloaded_files = self.files().get_downloaded_file()
        
        self.press_download()

        timeout = time.time() + self.timeout
        while time.time() < timeout:
            file = self.files().get_downloaded_file() - downloaded_files
            
            if file:
                file_name = max(file, key=os.path.getctime)
                
                if not file_name.endswith('.crdownload'):
                    self.logger.info(f"Download concluído: {file_name}")
                    return file_name
                else:
                    time.sleep(1)
                    continue
        
        return None


        

