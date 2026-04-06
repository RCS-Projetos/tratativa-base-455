
from .selenium import Driver
from .functions import Tools
from .functions.logger import Logger

class ReportSSW:
    def __init__(self, driver: Driver):
        self.logger = Logger()
        self.driver = driver
        
    def use_initial_parameters(self, branch: str, report: str, time: float = 0.5):
        inputs = [
            ('/html/body/form/input[1]', branch),
            ('/html/body/form/input[2]', report),
        ]

        set_branch = self.driver.wait_until(inputs[0][0])
        self.driver.execute_script('arguments[0].value = arguments[1]', set_branch, inputs[0][1])

        set_report = self.driver.wait_until(inputs[1][0])
        for char in inputs[1][1]:
            set_report.send_keys(char)
            time.sleep(time)


    def report_ssw(self):
        #Sobrescreva a lógica de uso do relatório
        ...