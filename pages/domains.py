# import streamlit as st
# import requests
# import pandas as pd

# st.set_page_config(layout="wide")

# API_URL = "http://localhost:8000/sms?month="

# MONTH_OPTIONS = {
#     "Março": "3.%20Março",
#     "Abril": "04.%20Abril",
#     "Maio": "05.%20Maio",
#     "Junho": "06.%20Junho",
#     "Julho": "07.%20Julho",
#     "Agosto": "08.%20Agosto",
#     "Setembro": "09.%20Setembro",
#     "Outubro": "10.%20Outubro",
#     "Novembro": "11.%20Novembro",
#     "Dezembro": "12.%Dezembro"
# }

# def get_local_datename():
#     import datetime
#     import locale
#     locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
#     return datetime.datetime.now().strftime('%B').capitalize()

# if 'selected_month_key' not in st.session_state:
#     st.session_state.selected_month_key = get_local_datename()
    
# if 'api_response' not in st.session_state:
#     st.session_state.api_response = {}

# @st.fragment(run_every=30)
# def fetch_and_compare_data():
#     """
#     Busca dados da API e compara com o st.session_state.
#     Se os dados forem diferentes, força um st.rerun() para atualizar a tela.
#     """
#     try:
#         api_month_value = MONTH_OPTIONS[st.session_state.selected_month_key]
        
#         response = requests.get(API_URL + api_month_value)
#         response.raise_for_status() # Verifica se houve erro HTTP
#         new_data = response.json().get("result", {})

#         old_data = st.session_state.api_response

#         if new_data != old_data:
#             st.session_state.api_response = new_data
#             st.rerun()

#     except requests.exceptions.RequestException as e:
#         st.toast(f"Erro ao conectar na API: {e}", icon="🔥")
#     except Exception as e:
#         st.toast(f"Erro ao processar dados: {e}", icon="⚠️")

# st.selectbox(
#     "Selecione o Mês:",
#     options=MONTH_OPTIONS.keys(),
#     key='selected_month_key'
# )

# fetch_and_compare_data()
# print(st.session_state.api_response)

# df = pd.DataFrame.from_dict(st.session_state.api_response, orient="index")
# df = df.stack().reset_index()
# st.dataframe(df)

# st.divider()

# if not st.session_state.api_response:
#     st.info("Aguardando dados da API...")
# else:
#     for key, values in st.session_state.api_response.items():
#         with st.container(border=True):
#             st.write(f"**{key}**")
#             st.write(values)