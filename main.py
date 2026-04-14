from report import Report
from ssw.selenium import Driver
from fastapi import FastAPI, BackgroundTasks
import threading
import logging
import time
from datetime import datetime, timedelta
import calendar
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger("Automação - 455")

app = FastAPI()

class RoboRequest(BaseModel):
    data_inicial: Optional[str] = None
    data_final: Optional[str] = None

def executar_automacao(d_inicial: str, d_final: str, documents:str = 'new'):
    report = Report(Driver(), documents)
    
    args = [
        {'key': 'cod_emp_ctb', 'value': '00'},
        {'key': 'f3', 'value': 'A'},
        {'key': 'f5', 'value': 'R'},
        {'key': 'f8', 'value': 'T'},
        {'key': 'f11', 'value': d_inicial},
        {'key': 'f12', 'value': d_final},
        {'key': 'f18', 'value': 'T'},
        {'key': 'f19', 'value': 'T'},
        {'key': 'f20', 'value': 'S'},
        {'key': 'f21', 'value': 'X'},
        {'key': 'f22', 'value': 'T'},
        {'key': 'f23', 'value': 'A'},
        {'key': 'f25', 'value': 'T'},
        {'key': 'f26', 'value': 'A'},
        {'key': 'f27', 'value': 'A'},
        {'key': 'f28', 'value': 'T'},
        {'key': 'ibscbs', 'value': 'A'},
        {'key': 'f29', 'value': 'A'},
        {'key': 'f30', 'value': 'A'},
        {'key': 'f35', 'value': 'E'},
        {'key': 'f37', 'value': 'B'},
        {'key': 'f38', 'value': 'F'},
        {'key': 'basico', 'value': 'N'},
    ]

    report.build_args(args, act='E1', dummy='1774980313075')
    report.execute_report(url = 'https://sistema.ssw.inf.br/bin/ssw0230')
    report.process_report()

def subtrair_um_mes(dt: datetime) -> datetime:
    year = dt.year
    month = dt.month - 1
    if month == 0:
        year -= 1
        month = 12
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)

def executar_historico(d_inicial: str, d_final: str):
    data_inicial = datetime.strptime(d_inicial, "%d%m%y")
    data_final = datetime.strptime(d_final, "%d%m%y")
    
    # Não pode ultrapassar a data atual
    if data_final > datetime.now():
        data_final = datetime.now()
        
    current_end = data_final
    
    while current_end > data_inicial:
        current_start = subtrair_um_mes(current_end)
        if current_start < data_inicial:
            current_start = data_inicial
            
        try:
            logger.info(f"Executando automação para a data: {current_start.strftime('%d/%m/%Y')} até {current_end.strftime('%d/%m/%Y')}")
            executar_automacao(current_start.strftime("%d%m%y"), current_end.strftime("%d%m%y"), 'all')
        except Exception as e:
            logger.error(f"Erro ao executar automação para o período: {current_start.strftime('%d/%m/%Y')} até {current_end.strftime('%d/%m/%Y')}")
            logger.error(str(e))
            
        current_end = current_start


@app.post("/executar/")
def trigger_robo(background_tasks: BackgroundTasks):
    start_date = (datetime.now() - timedelta(days=30)).strftime("%d%m%y")
    end_date = datetime.now().strftime("%d%m%y")
    background_tasks.add_task(executar_automacao, start_date, end_date)
    return {"mensagem": "Robô acionado com sucesso e rodando em background!"}

@app.post("/historico/")
def trigger_robo(payload: RoboRequest, background_tasks: BackgroundTasks):
    d_inicial = payload.data_inicial
    d_final = payload.data_final
    
    background_tasks.add_task(executar_historico, d_inicial, d_final)
    return {"mensagem": "Robô de histórico acionado com sucesso e rodando em background!"}


@app.get("/")
def health():
    return {"status": "online", "service": "Ingestão Relatório 930"}


