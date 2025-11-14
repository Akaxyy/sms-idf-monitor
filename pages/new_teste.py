import streamlit as st
import pandas as pd

# --- 1. Nossos Dados (Simulação de BD) ---
data = {
    'nome': ['Ana', 'Bruno', 'Carla', 'Daniel', 'Elisa', 'Fabio'],
    'cargo': ['Admin', 'Analista', 'Analista', 'Gerente', 'Gerente', 'Admin'],
    'salario': [15000, 7000, 7200, 12000, 12500, 15500]
}
df_salarios = pd.DataFrame(data)

# Lista completa de cargos que existem na base
todos_os_cargos = df_salarios['cargo'].unique()
# Resultado: ['Admin', 'Analista', 'Gerente']


# --- 2. Simulação de Autenticação ---
# Em um app real, isso viria de st.session_state após o login
st.sidebar.title("Simulação de Login")
usuario_logado_cargo = st.sidebar.selectbox(
    "Selecione o usuário (Logado como):",
    options=todos_os_cargos,
    index=0 # Começa logado como 'Admin'
)
st.sidebar.divider() # Adiciona uma linha divisória


# --- 3. Lógica de Permissão (A CHAVE!) ---
# Aqui definimos quais opções o usuário poderá ver no filtro

if usuario_logado_cargo == 'Admin':
    # O Admin pode ver todos os cargos no filtro
    opcoes_para_o_filtro = todos_os_cargos
    # O padrão do filtro para o Admin é ver tudo
    default_do_filtro = todos_os_cargos
else:
    # Qualquer outro usuário só pode ver o seu próprio cargo
    opcoes_para_o_filtro = [usuario_logado_cargo]
    # O padrão é já vir selecionado
    default_do_filtro = [usuario_logado_cargo]


# --- 4. O Multiselect Dinâmico ---
st.sidebar.title("Filtros do Relatório")

# Passamos as opções que definimos na lógica acima
cargos_selecionados = st.sidebar.multiselect(
    "Filtrar por Cargo:",
    options=opcoes_para_o_filtro,
    default=default_do_filtro
)


# --- 5. Filtrar o DataFrame ---
# A filtragem final usa a seleção (segura) do multiselect
df_filtrado = df_salarios[df_salarios['cargo'].isin(cargos_selecionados)]


# --- 6. Exibir Resultados ---
st.title("Relatório de Salários 💰")
st.write(f"Você está logado como: **{usuario_logado_cargo}**")
st.write("Cargos selecionados no filtro:", cargos_selecionados)

st.dataframe(df_filtrado)