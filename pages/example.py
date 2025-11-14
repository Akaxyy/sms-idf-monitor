from turtle import width
import streamlit as st
import requests
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Nome": ["Ana", "Bruno", "Carlos"],
    "Idade": [23, 31, 19],
    "Cidade": ["SP", "RJ", "BH"]
})

df2 = pd.DataFrame({
    "Produto": ["Parafuso", "Porca", "Arruela"],
    "Estoque Atual": [100, 150, 200],
    "Preço Unitário": [0.5, 0.3, 0.2],
})

## ST.DATAFRAME - SETUP
st.write("### Pessoas:")
# Filtros interativos
st.sidebar.header("Filtros")
nome = st.sidebar.multiselect("Filtrar por nome:", df["Nome"].unique())
cidade = st.sidebar.multiselect("Filtrar por cidade:", df["Cidade"].unique())

df_filtrado = df.copy()
if nome:
    df_filtrado = df_filtrado[df_filtrado["Nome"].isin(nome)]
if cidade:
    df_filtrado = df_filtrado[df_filtrado["Cidade"].isin(cidade)]

st.dataframe(
    df_filtrado.style.background_gradient(
        subset="Idade", cmap="Greens"
    ),
    hide_index=True,
)

## ST.DATA_EDITOR - SETUP
st.write("### Estoque:")
editado = st.data_editor(
    df2,
    num_rows="dynamic",
    key="editor_estoque",
    column_config={
        "Produto": st.column_config.TextColumn("Produto", help="Nome do Item"),
        "Estoque Atual": st.column_config.NumberColumn("Qtd", help="Quantidade Disponivel", min_value=0),
        "Preço Unitário": st.column_config.NumberColumn("Preço (R$)", format="%.2f", step=0.1),
    },
    hide_index=True,
)

editado["Valor Total (R$)"] = (editado["Estoque Atual"] * editado["Preço Unitário"]).round(2)
st.write("### Estoque atualizado:")
st.dataframe(editado, width="stretch", hide_index=True)

if st.button("Salvar Alterações"):
    st.success("Alteraçoes salvas com sucesso!")
    st.write("Dados finais:")
    st.table(editado)


# # Feedback ao enviar (POST Method)
# def http_post(nome, email, mensagem):
#     dados = {"nome": nome, "email": email, "mensagem": mensagem}

#     try:
#         resposta = requests.post("http://127.0.0.1:8000/enviar", json=dados)
#         if resposta.status_code == 200:
#             st.success(resposta.json()["mensagem"])
#         else:
#             st.error("Erro ao enviar os dados para o backend.")
#     except Exception as e:
#         st.error(f"Falha na conexão: {e}")

# Configuração da página
st.set_page_config(page_title="Formulário Azul Moderno", layout="centered")

# Container centralizado
with st.container():
    st.subheader("Entre em Contato", help="Testando", divider=True)
    st.write("Preencha o formulário abaixo e enviaremos sua mensagem para o backend.")

# Formulário usando colunas para organização
with st.form("_form"):
    st.subheader("Envie sua mensagem")

    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome")
        email = st.text_input("Email")
    
    with col2:
        mensagem = st.text_area("Mensagem", height=120)

    st.divider()
    enviar = st.form_submit_button("Enviar !", width="stretch", type="primary") #on_click=http_post(nome, email, mensagem))

# Mostrar respostas anteriores em expander
if st.checkbox("Mostrar respostas recebidas"):
    with st.expander("Clique para ver as mensagens recebidas"):
        # Aqui você poderia buscar do backend ou banco de dados
        st.info("Exemplo de mensagem: 'Olá, recebi sua mensagem!'")

