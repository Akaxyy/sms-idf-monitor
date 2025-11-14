import streamlit as st
import pandas as pd
import json
from io import StringIO

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Plataforma de Auditoria")
st.title("Plataforma de Upload para Auditoria")

# --- Carregamento dos Dados ---
@st.cache_data
def carregar_dados():
    return pd.read_json("./static/data.json", orient='index')

df = carregar_dados()

# --- Barra Lateral com Filtros ---
st.sidebar.header("Filtros de Visualização")
 
# Filtro por Setor
setores_unicos = df['SETOR'].unique()
setor_selecionado = st.sidebar.multiselect(
    'Selecione o Setor:',
    options=setores_unicos,
    default=setores_unicos
)

df_filtrado_setor = df[df['SETOR'].isin(setor_selecionado)]

responsaveis_flat = df_filtrado_setor['RESPONSÁVEL'].explode()
responsaveis_validos = [r for r in responsaveis_flat.unique() if pd.notna(r)]

responsavel_selecionado = st.sidebar.multiselect(
    'Selecione o Responsável:',
    options=responsaveis_validos,
    default=responsaveis_validos
)

# --- Lógica de Filtragem ---
# Filtra por setor
df_filtrado = df[df['SETOR'].isin(setor_selecionado)]

# Filtra por responsável: checa se CADA item da lista de responsáveis da linha
# contém PELO MENOS UM dos responsáveis selecionados no filtro.
df_filtrado = df_filtrado[
    df_filtrado['RESPONSÁVEL'].apply(
        lambda lista_resp_linha: any(resp in lista_resp_linha for resp in responsavel_selecionado)
    )
]

# --- Renderização Dinâmica dos Itens ---
st.header("Itens para Análise")

if df_filtrado.empty:
    st.warning("Nenhum item encontrado com os filtros selecionados.")
else:
    # Itera sobre cada linha (item) do DataFrame que passou pelo filtro
    for index, row in df_filtrado.iterrows():
        
        st.subheader(f"Item: {row['ITEM']}")
        st.markdown(f"**Pergunta Principal:** {row['PERGUNTA']}")

        # Usando um expander para manter a interface limpa
        with st.expander("Clique para ver os detalhes e enviar documentos"):

            # Colunas para organizar as informações do item
            col1, col2 = st.columns([1, 2])
            with col1:
                st.info(f"**Setor:** {row['SETOR']}")
                # 'join' transforma a lista de responsáveis em uma string bonita
                st.info(f"**Responsáveis:** {', '.join(row['RESPONSÁVEL'])}")
                st.info(f"**Prazo:** {row['DATA']}")

            with col2:
                st.markdown("**Documentos de Referência:**")
                # Itera e exibe a lista de documentos
                for doc in row['DOCUMENTOS']:
                    st.markdown(f"- {doc}")

            st.markdown("---")
            st.markdown("### 📥 Documentação Necessária (Upload)")

            #
            # Esta é a lógica principal de VINCULAÇÃO
            #
            perguntas_necessarias = row['DOCUMENTOS NECESSÁRIOS']
            
            # Itera sobre cada pergunta na lista "DOCUMENTOS NECESSÁRIOS"
            for q_index, pergunta_doc in enumerate(perguntas_necessarias):
                
                # 1. CRIA A CHAVE ÚNICA:
                # Esta chave é o VÍNCULO. Ex: "upload_1.1.1_0", "upload_1.1.1_1", etc.
                unique_key = f"upload_{row['ITEM']}_{q_index}"
                
                # 2. CRIA O WIDGET DE UPLOAD COM A CHAVE
                # O Streamlit armazena automaticamente o arquivo enviado em 
                # st.session_state[unique_key]
                st.file_uploader(
                    pergunta_doc,  # O label é a própria pergunta
                    key=unique_key,
                    type=['pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'docx', 'msg', 'zip']
                )
        
        st.markdown("---") # Separador horizontal entre os itens

# --- Botão de Processamento (Para provar o vínculo) ---
st.header("Resultados do Vínculo")
st.markdown(
    "Use os campos acima, envie alguns arquivos e clique no botão abaixo "
    "para ver como o sistema vinculou cada arquivo a uma chave única."
)

if st.button("Processar e Ver Vínculos"):
    st.markdown("### Arquivos Vinculados na Sessão:")
    
    arquivos_encontrados = False
    
    # Iteramos por TUDO que o Streamlit tem na memória da sessão
    for key, uploaded_file in st.session_state.items():
        
        # Filtramos apenas pelas chaves que criamos
        if key.startswith("upload_") and uploaded_file is not None:
            arquivos_encontrados = True
            # Exibe a prova do vínculo
            st.success(f"**Chave:** `{key}` **--> Arquivo:** `{uploaded_file.name}`")
            
    if not arquivos_encontrados:
        st.warning("Nenhum arquivo foi enviado ainda.")