import os
import logging
from typing import final
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext


class Driver:
    def __init__(self, headless: bool = True, download_dir: str = 'Downloads'):
        self.__logger = logging.getLogger('driver_websockets')
        self.__logger.info(f'Iniciando Driver com headless={headless} e download_dir={download_dir}')
        
        self._download_dir = os.path.abspath(download_dir)
        self.ensure_download_dir()
        
        self.__playwright = sync_playwright().start()
        self.__browser: Browser = self.__playwright.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        self.__context: BrowserContext = self.__browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            accept_downloads=True # Habilita downloads
        )

        self.__page: Page = self.__context.new_page()

    @final
    def ensure_download_dir(self):
        if not os.path.exists(self._download_dir):
            os.makedirs(self._download_dir)
            self.__logger.info(f'Directory {self._download_dir} created')
    
    @final
    def get(self, url: str):
        self.__logger.info(f'Acessando {url}')
        self.__page.goto(url, wait_until='domcontentloaded')
        self.__page.wait_for_load_state('domcontentloaded')
        self.__logger.info(f'URL {url} acessada com sucesso')
        return {'status': 'success', 'message': f'URL {url} acessada com sucesso'}
    
    @final
    def quit(self):
        self.__logger.info('Fechando driver')
        self.__context.close()
        self.__browser.close()
        self.__playwright.stop()
        return {'status': 'success', 'message': 'Driver fechado com sucesso'}
    
    @property
    def page(self) -> Page:
        return self.__page

    @property
    def download_path(self) -> str:
        return self._download_dir 