from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from folder_analyzer import montar_relatorio_sms
from pathlib import Path
from os import getlogin

app = FastAPI(title="API - C3", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho base que será analisado

@app.get("/sms")
def verificar_sms(month: str = Query(..., description="Ex: 10. Outubro ou 11. Novembro")):
    """
    Executa a verificação do diretório SMS e retorna o relatório.
    """
    BASE_PATH = Path(fr"C:/Users/{getlogin()}/C3 ENGENHARIA/C3 Engenharia SEDE - 3.1.30 - IDF/{month}")

    if not BASE_PATH.exists():
        return {"status": "erro", "messagem": f"O mês '{month}' não foi encontrado em {BASE_PATH}"}

    relatorio = montar_relatorio_sms(BASE_PATH)
    return {"status": "ok", "result": relatorio, "path": BASE_PATH}
