import itertools
import streamlit as st
import pandas as pd
from static.svg_icons import * # Supondo que isso importe os SVGs
import json
import requests

# =============================================================================
# 1. FUNÇÕES DE CARREGAMENTO DE DADOS E CONFIGURAÇÃO
# (Ideal para substituir por chamadas de back-end)
# =============================================================================

def load_css(file_path):
    """Carrega um arquivo CSS"""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo CSS não encontrado: {file_path}")

@st.cache_data
def get_data_setores():
    """(PLACEHOLDER) Retorna dados fictícios de setores."""
    # TODO: Substituir por chamada de API ou consulta real
    return pd.DataFrame({
        "Setor": ["SMS", "QUALIDADE", "PRAZO", "GESTÃO"],
        "Itens": [2, 7, 1, 1]
    })

@st.cache_data
def get_data_responsaveis():
    """(PLACEHOLDER) Retorna dados fictícios de responsáveis."""
    # TODO: Substituir por chamada de API ou consulta real
    return pd.DataFrame({
        "Sigla": ["LE", "AL", "TA", "JO"],
        "Avatar": ["avatar-le", "avatar-al", "avatar-ta", "avatar-jo"],
        "Nome": ["Leonardo / Nathalia", "Alex", "Tadeu", "João"],
        "Itens": ["3 itens", "5 itens", "1 item", "3 itens"]
    })

@st.cache_data
def carregar_dados_principais():
    """Carrega dados do JSON."""
    try:
        with open("./static/data.json", 'r', encoding="utf-8") as f:
            item_map = json.load(f)
        return pd.DataFrame.from_dict(item_map, orient="index").reset_index(drop=True)
    except Exception as e:
        st.error(f"Erro ao carregar data.json: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_secundarios():
    """Carrega dados do CSV."""
    try:
        return pd.read_csv("static/aleatorio.csv", sep=",")
    except Exception as e:
        st.error(f"Erro ao carregar aleatorio.csv: {e}")
        return pd.DataFrame()

# =============================================================================
# 2. FUNÇÕES DE PROCESSAMENTO DE DADOS
# (Lógica de negócio e transformações)
# =============================================================================

def normalizar_responsavel(x):
    """Transforma a coluna 'RESPONSAVEL' em uma lista limpa."""
    if isinstance(x, list):
        if len(x) == 1 and isinstance(x[0], list):  # caso [[...]]
            x = x[0]
        if len(x) == 1 and isinstance(x[0], str) and "/" in x[0]:
            x = x[0].replace(" ", "").split("/")
    elif isinstance(x, str):
        if "/" in x:
            x = x.replace(" ", "").split("/")
        else:
            x = [x]
    else:
        x = []
    return x

def preparar_dados_bi(df_principal, df_secundario):
    """Mescla e normaliza os dados para a aba de BI."""
    if df_principal.empty or df_secundario.empty:
        return pd.DataFrame()
        
    df_tab1 = pd.merge(df_principal, df_secundario, how="inner", on="ITEM")
    df_tab1["RESPONSAVEL"] = df_tab1["RESPONSAVEL"].apply(normalizar_responsavel)
    return df_tab1

# =============================================================================
# 3. COMPONENTES DE UI (POPUPS / DIALOGS)
# =============================================================================

@st.dialog("Detalhes do Setor")
def show_itens_setor(setor, itens):
    st.write(f"### {setor}")
    st.write("Itens relacionados:")

    for i in range(1, itens + 1):
        st.markdown(f"- Item {i} do setor {setor}")

    if st.button("Fechar", key=f"close_setor_{setor}", use_container_width=True):
        st.session_state.pop("popup_setor", None)
        st.rerun()

@st.dialog("Itens do Responsável")
def show_itens_responsavel(nome, itens_text):
    st.write(f"### {nome}")
    st.write("Itens atribuídos:")

    try:
        count = int(str(itens_text).split()[0])
    except Exception:
        count = 0

    if count == 0:
        st.write("Nenhum item atribuído.")
    else:
        for i in range(1, count + 1):
            st.markdown(f"- Item {i} de {nome}")

    if st.button("Fechar", key=f"close_resp_{nome}", use_container_width=True):
        st.session_state.pop("popup_resp", None)
        st.rerun()

# =============================================================================
# 4. COMPONENTES DE UI (WIDGETS REUTILIZÁVEIS)
# =============================================================================

def render_metric_card(label, value, delta, icon_svg_string, icon_bg_class, delta_color="normal"):
    """Renderiza os cards superiores"""
    with st.container(border=True):
        col1_metric, col2_icon = st.columns([2.5, 1], vertical_alignment="top", gap="large")
        with col1_metric:
            st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
        with col2_icon:
            st.markdown(f"""
                <div class="icon-background {icon_bg_class}"> {icon_svg_string}</div>
            """, unsafe_allow_html=True)

def render_setor_row(setor, itens, max_itens):
    """Renderiza a linha do setor"""
    percent = int((itens / max_itens) * 100) if max_itens > 0 else 0
    col_html, col_btn = st.columns([1, 0.1], vertical_alignment="center") 

    with col_html:
        html = f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px; width: 100%;">
            <div style="min-width: 100px; max-width: 100px;">
                <span class="setor-label">{setor}</span>
            </div>
            <div style="flex: 1;">
                <div class="setor-bar-container">
                    <div class="setor-bar" style="width: {percent}%;"></div>
                </div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        
    with col_btn:
        if st.button(f"{itens}", key=f"setor_{setor}"):
            st.session_state["popup_setor"] = (setor, itens)
            st.rerun()

def render_responsavel_row(sigla, avatar_class, nome, itens_text):
    """Renderiza a linha do responsável"""
    col_html, col_btn = st.columns([4, 1], vertical_alignment="center") 

    with col_html:
        html = f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; width: 100%;">
            <div style="min-width: 40px; max-width: 40px;">
                <div class="avatar {avatar_class}">{sigla}</div>
            </div>
            <div style="flex: 1;">
                <div class="responsavel-info">
                    <div class="responsavel-nome">{nome}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        
    with col_btn:
        if st.button(f"{itens_text}", key=f"resp_{nome}"):
            st.session_state["popup_resp"] = (nome, itens_text)
            st.rerun()

def render_bi_item(item_row):
    """Renderiza um único card de item na aba BI & Análise."""
    item = item_row  # Para manter a semelhança com o loop original
    
    with st.container(border=True):
        col1, col2 = st.columns([9, 1], vertical_alignment="top")

        # ======================
        # COLUNA ESQUERDA
        # ======================
        with col1:
            top_col1, top_col2 = st.columns([1, 13], vertical_alignment="top")

            # --- código do item ---
            with top_col1:
                st.markdown(
                    f"""
                    <span style="
                        background-color:#EEF4FF; color:#2563EB; font-weight:600;
                        padding:16px 14px; border-radius:8px; font-size:0.9rem;
                        display:inline-block;
                    ">{item['ITEM']}</span>
                    """,
                    unsafe_allow_html=True
                )

            # --- equipe e status ---
            with top_col2:
                match item["SETOR"]:
                    case "SMS": _color = "red"
                    case "QUALIDADE": _color = "blue"
                    case "PRAZO": _color = "orange"
                    case "GESTÃO": _color = "green"
                    case _: _color = "gray"
                
                match item["STATUS"]:
                    case "Concluido":
                        _color_hex = "#059669"
                        _icon_svg = 'fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd"'
                    case "Em andamento":
                        _color_hex = "#d97706"
                        _icon_svg = 'fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm.75-13a.75.75 0 0 0-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 0 0 0-1.5h-3.25V5Z" clip-rule="evenodd"'
                    case "Não enviado":
                        _color_hex = "#d91c1c"
                        _icon_svg = 'fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd"'
                    case _:
                        _color_hex = "#555"
                        _icon_svg = "" # Adicionar um ícone padrão se necessário

                st.badge(item["SETOR"], color=_color)
                st.markdown(
                    f"""
                    <div style="margin-top:-10px;">
                        <span style="
                            color:{_color_hex}; font-weight:500; font-size:0.9rem;
                            display:inline-flex; align-items:center; gap:6px;
                        ">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" 
                                viewBox="0 0 20 20" stroke-width="1.5" 
                                stroke="currentColor" width="16" height="16">
                                <path {_icon_svg} />
                            </svg>
                            {item["STATUS"]}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # --- texto principal ---
            st.markdown(
                f"""
                <p style="
                    font-size:0.95rem; color:#111827; font-weight:500;
                    line-height:1.4;
                ">
                    {item['PERGUNTA']}
                </p>
                """,
                unsafe_allow_html=True
            )

        # ======================
        # COLUNA DIREITA
        # ======================
        with col2:
            st.markdown(
                f"""
                <div style="text-align:right; font-size:1.5rem; font-weight:700; color:#111827;">
                    {item["PERCENTUAL"]}%
                </div>
                """,
                unsafe_allow_html=True
            )

            # --- barra progresso ---
            st.markdown(
                f"""
                <div style="
                    background-color:#E5E7EB; height:6px; width:100%;
                    border-radius:4px; overflow:hidden; margin-top:4px;
                ">
                    <div style="
                        width:{item["PERCENTUAL"]}%; height:100%;
                        background-color:#2563EB;
                    "></div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # --- Expander ---
        with st.expander("Ver detalhes e documentos"):
            st.write("📄 Aqui você pode colocar as evidências, anexos ou observações.")

        st.write("") # Espaçador

# =============================================================================
# 5. RENDERIZAÇÃO DAS PÁGINAS PRINCIPAIS (VIEWS)
# =============================================================================

def render_sidebar(df):
    """Renderiza a barra lateral e retorna as seleções."""
    st.sidebar.header("Filtros")
    
    setores_opcoes = df["SETOR"].unique()
    setores_sel = st.sidebar.multiselect("Selecione o Setor", options=setores_opcoes)
    
    st.sidebar.divider()
    
    # A lógica para obter responsáveis únicos é complexa, por isso está aqui
    responsaveis_opcoes = list(set(itertools.chain.from_iterable(df["RESPONSAVEL"])))
    resp_sel = st.sidebar.multiselect("Selecione o Responsável", options=sorted(responsaveis_opcoes))
    
    return setores_sel, resp_sel

def render_dashboard_tab(setores_sel, resp_sel):
    """Renderiza todo o conteúdo da aba 'Dashboard'."""
    
    # Header
    st.title("Dashboard de Análise - IDF")
    st.divider()

    # --- MÉTRICAS ---
    with st.container():
        card1, card2, card3, card4 = st.columns([2.5, 2.5, 2.5, 2.5])
        with card1:
            render_metric_card("Total de Itens", "24", "+2 (últ. dia)", ICON_ITENS, "icon-bg-blue")
        with card2:
            render_metric_card("Pendentes", "6", "-1 (últ. dia)", ICON_PENDENTES, "icon-bg-orange")
        with card3:
            render_metric_card("Concluídos", "16", "0.1%", ICON_CONCLUSAO, "icon-bg-green")
        with card4:
            render_metric_card("Taxa de Conclusão", "67%", "+3 (últ. dia)", ICON_TAXA, "icon-bg-cyan")

    # --- Dados principais (usando placeholders) ---
    df_setores = get_data_setores()
    df_resp = get_data_responsaveis()

    # Aplica filtros da sidebar (os mesmos filtros são usados na outra aba)
    df_setores_f = df_setores[df_setores["Setor"].isin(setores_sel)] if setores_sel else pd.DataFrame()
    
    # Nota: A filtragem de responsáveis aqui é baseada nos Nomes Fictícios.
    # A aba de BI usa os nomes normalizados. Isso pode ser unificado no futuro.
    df_resp_f = df_resp[df_resp["Nome"].isin(resp_sel)] if resp_sel else pd.DataFrame()


    col_setor, col_resp = st.columns(2)

    # --- Itens por Setor ---
    with col_setor:
        with st.container(border=True, height=300):
            st.subheader("Itens por Setor")
            if df_setores_f.empty:
                st.info("Selecione ao menos um setor na barra lateral.")
            else:
                max_itens = df_setores_f["Itens"].max()
                for _, row in df_setores_f.iterrows():
                    render_setor_row(row["Setor"], int(row["Itens"]), max_itens)

    # --- Responsáveis Ativos ---
    with col_resp:
        with st.container(border=True, height=300):
            st.subheader("Responsáveis Ativos")
            if df_resp_f.empty:
                st.info("Selecione ao menos um responsável na barra lateral.")
            else:
                for _, row in df_resp_f.iterrows():
                    render_responsavel_row(row["Sigla"], row["Avatar"], row["Nome"], row["Itens"])

    # --- Lógica de Popups (só é ativada por cliques nos componentes) ---
    if "popup_setor" in st.session_state:
        setor_param, itens_val = st.session_state["popup_setor"]
        show_itens_setor(setor_param, itens_val)

    if "popup_resp" in st.session_state:
        resp_param, itens_text = st.session_state["popup_resp"]
        show_itens_responsavel(resp_param, itens_text)

def render_bi_tab(df_base_normalizada, setores_sel, resp_sel):
    """Renderiza todo o conteúdo da aba 'BI & Análise'."""
    
    if df_base_normalizada.empty:
        st.error("Dados de BI não puderam ser carregados. Verifique os arquivos CSV e JSON.")
        return

    # -----------------------------
    # 1. FILTRAGEM DA SIDEBAR (EM CIMA DOS DADOS JÁ NORMALIZADOS)
    # -----------------------------
    df_base_aba = df_base_normalizada.copy()

    if resp_sel:
        df_base_aba = df_base_aba[df_base_aba["RESPONSAVEL"].apply(
            lambda lista: any(resp in lista for resp in resp_sel)
        )]
    
    if setores_sel:
        df_base_aba = df_base_aba[df_base_aba["SETOR"].isin(setores_sel)]

    # -----------------------------
    # 2. FILTROS DA ABA (EM CASCATA)
    # -----------------------------
    with st.container(border=True): # horizontal=True removido para melhor compatibilidade
        
        filter_cols = st.columns(2)
        
        # --- FILTRO DE STATUS ---
        with filter_cols[0]:
            status_opcoes = sorted(df_base_aba["STATUS"].unique())
            filtro_status = st.selectbox(
                "Status", 
                status_opcoes, 
                index=None, 
                placeholder="Status..."
            )

        # --- FILTRO DE ITEM (DINÂMICO) ---
        if filtro_status:
            df_para_itens = df_base_aba[df_base_aba["STATUS"] == filtro_status]
        else:
            df_para_itens = df_base_aba.copy()
        
        item_opcoes_dinamicas = sorted(df_para_itens["ITEM"].unique())
        
        with filter_cols[1]:
            filtro_item = st.selectbox(
                "Item", 
                item_opcoes_dinamicas, # <-- Opções dinâmicas
                index=None, 
                placeholder="Item..."
            )

    # -----------------------------
    # 3. APLICAÇÃO FINAL DOS FILTROS
    # -----------------------------
    df_final = df_base_aba.copy()

    if filtro_status:
        df_final = df_final[df_final["STATUS"] == filtro_status]

    if filtro_item:
        df_final = df_final[df_final["ITEM"] == filtro_item]

    # -----------------------------
    # 4. DEBUG (Opcional)
    # -----------------------------
    with st.expander("DEBUG"):
        st.subheader("⚙️ DEBUG - Dados Filtrados")
        st.write("Filtros da Sidebar:", {"Setores": setores_sel, "Responsáveis": resp_sel})
        st.write("Filtros da Aba:", {"Status": filtro_status, "Item": filtro_item})
        st.write(df_final[["ITEM", "RESPONSAVEL", "SETOR", "STATUS"]].head(25))

    # -----------------------------
    # 5. RENDERIZAÇÃO DE ITENS
    # -----------------------------
    if df_final.empty:
        st.info("Nenhum item encontrado com os filtros selecionados.")
    else:
        for _, item in df_final.iterrows():
            render_bi_item(item) # Chama a função de componente reutilizável


# =============================================================================
# 6. APLICAÇÃO PRINCIPAL (MAIN)
# =============================================================================

def main():
    """Função principal que executa o app Streamlit."""
    
    # --- Configurações Iniciais ---
    # st.set_page_config deve ser a primeira chamada
    st.set_page_config(page_title="IDF - Visão Analítica", layout="wide", page_icon="assets/logo.png")
    load_css("static/style.css")

    # --- Carregamento e Preparação de Dados ---
    # Carrega os dados uma vez
    df_principal = carregar_dados_principais()
    df_secundario = carregar_dados_secundarios()
    
    # Prepara os dados para a Aba 2 (inclui normalização)
    df_bi_normalizado = preparar_dados_bi(df_principal, df_secundario)

    # --- Renderização da Sidebar ---
    # Passamos os dados normalizados para a sidebar extrair os filtros corretamente
    setores_sel, resp_sel = render_sidebar(df_bi_normalizado)

    # --- Renderização das Abas ---
    tabs = st.tabs(['Dashboard', 'BI & Análise'])
    
    with tabs[0]:
        # A Aba 1 usa seus próprios dados placeholder, mas aplica os filtros da sidebar
        render_dashboard_tab(setores_sel, resp_sel)
        
    with tabs[1]:
        # A Aba 2 usa os dados reais e os filtros da sidebar
        render_bi_tab(df_bi_normalizado, setores_sel, resp_sel)

if __name__ == "__main__":
    main()