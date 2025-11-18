import subprocess
import requests
import pandas as pd
import streamlit as st

# URL da sua API (exemplo)
API_URL = "http://127.0.0.1:8000/sms?month=11.%20Novembro"

def fetch_data():
    """Busca os dados originais da API."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json().get("result", {})
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar na API: {e}")
        return {}
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        return {}

print("Buscando dados da API...")
data = fetch_data()

st.json(data.get("result"))
