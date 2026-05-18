from src.ssw.report import Report
from src.websocket import Driver
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() # Garante que saia no terminal
    ]
)


payload = [
        {'xpath': 'xpath=/html/body/form/input[10]', 'value': '010526'},
        {'xpath': 'xpath=/html/body/form/input[11]', 'value': '110526'},
        {'xpath': 'xpath=/html/body/form/input[31]', 'value': 'E'},
        {'xpath': 'xpath=/html/body/form/input[32]', 'value': 'B'},
        {'xpath': 'xpath=/html/body/form/input[33]', 'value': 'F'},
    ]

report = Report(Driver(headless=False),'455', 'https://sistema.ssw.inf.br/bin/ssw0230', payload, 'xpath=/html/body/form/a[2]')
report.run()