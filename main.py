from report import Report
from ssw.selenium import Driver
from fastapi import FastAPI, BackgroundTasks
import threading
import logging
import time
from datetime import datetime, timedelta
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

def executar_historico(d_inicial: str, d_final: str):
    data_inicial = datetime.strptime(d_inicial, "%d%m%y")
    data_final = datetime.strptime(d_final, "%d%m%y")
    
    while data_inicial <= data_final:
        try:
            logger.info(f"Executando automação para a data: {data_inicial.strftime('%d/%m/%Y')} até {(data_inicial + timedelta(days=30)).strftime('%d/%m/%Y')}")
            executar_automacao(data_inicial.strftime("%d%m%y"), (data_inicial + timedelta(days=30)).strftime("%d%m%y"), 'all')
            data_inicial += timedelta(days=30)
            data_inicial = datetime.now() if data_inicial > datetime.now() else data_inicial
        except Exception as e:
            logger.error(f"Erro ao executar automação para a data: {data_inicial.strftime('%d/%m/%Y')}")
            logger.error(str(e))
            continue


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


