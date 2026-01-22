from fastapi import FastAPI
import threading
import logging
import time

from functions import make_login, driver
from treatments import treat_455, treat_file_455


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Robo-455")

app = FastAPI()


def ingestao():
    logger.info("🚀 Iniciando ingestão do 455")
    driver_chr = None
    
    try:
        logger.info("Abrindo navegador...")
        driver_chr = driver()

        logger.info("Fazendo login...")
        make_login(driver_chr)
        time.sleep(3)

        logger.info("Tratando arquivo...")
        new_file = treat_455(driver_chr)

        logger.info("Tratando arquivo e enviando para Produção...")
        treat_file_455(new_file)

    except Exception as e:
        logger.error(f"Erro ao processar o 455: {str(e)}")
    
    finally:
        if driver_chr:
            driver_chr.quit()
            logger.info("Navegador fechado.")


@app.post("/executar")
def trigger_robo():
    if threading.active_count() > 5:
        return {"message": "Já existem 5 ingestões em andamento. Aguarde as ingestões anteriores terminarem."}
    
    t = threading.Thread(target=ingestao)
    t.start()
    return {"status": "iniciado", "message": "Robô rodando em background"}

@app.get("/")
def health():
    return {"status": "online", "service": "Ingestão Relatório 455"}