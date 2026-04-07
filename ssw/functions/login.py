import time
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from ..selenium import Driver
from .logger import Logger


class Login:
    def __init__(
        self,
        driver: Driver,
        company: str,
        tax: str,
        user: str,
        password: str,
        url: str = 'https://sistema.ssw.inf.br/bin/ssw0422',
        campany_xpath: str = '/html/body/form/input[1]',
        tax_xpath: str = '/html/body/form/input[2]',
        user_xpath: str = '/html/body/form/input[3]',
        password_xpath: str = '/html/body/form/input[4]',
        send_xpath: str = '/html/body/form/a',
        wait: int = 20
    ):
        self.logger = Logger()
        self._driver = driver
        self.company = company
        self.tax = tax
        self.user = user
        self.password = password
        self.url = 'https://sistema.ssw.inf.br/bin/ssw0422'
        self.campany_xpath = campany_xpath
        self.tax_xpath = tax_xpath
        self.user_xpath = user_xpath
        self.password_xpath = password_xpath
        self.send_xpath = send_xpath
        self.wait = wait


    def login(self):
        self.logger.info("Iniciando processo de login")
        self._driver.get(self.url)

        inputs = [
            (self.campany_xpath, self.company),
            (self.tax_xpath, self.tax),
            (self.user_xpath, self.user),
            (self.password_xpath, self.password)
        ]

        for xpath, value in inputs:
            input = self._driver.wait_until(xpath)
            self._driver.execute_script(input, value)
        
        send = self._driver.wait_until(self.send_xpath)
        send.click()
        self.logger.info("Login submetido")
        









