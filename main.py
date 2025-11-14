import itertools
import streamlit as st
import pandas as pd
from static.svg_icons import *
import json


# --- FUNÇÕES UTILITÁRIAS ---
def load_css(file_path):
    """Carrega um arquivo CSS"""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo CSS não encontrado: {file_path}")

def get_data_setores():
    """(PLACEHOLDER) Retorna dados fictícios de setores."""
    return pd.DataFrame({
        "Setor": ["SMS", "QUALIDADE", "PRAZO", "GESTÃO"],
        "Itens": [2, 7, 1, 1]
    })

def get_data_responsaveis():
    """(PLACEHOLDER) Retorna dados fictícios de responsáveis."""
    return pd.DataFrame({
        "Sigla": ["LE", "AL", "TA", "JO"],
        "Avatar": ["avatar-le", "avatar-al", "avatar-ta", "avatar-jo"],
        "Nome": ["Leonardo / Nathalia", "Alex", "Tadeu", "João"],
        "Itens": ["3 itens", "5 itens", "1 item", "3 itens"]
    })

# --- POPUPS --- 
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

@st.cache_data
def carregar_dados():
    with open("./static/data.json", 'r', encoding="utf-8") as f:
        return json.load(f)

# --- COMPONENTES VISUAIS ---
def render_metric_card(label, value, delta, icon_svg_string, icon_bg_class, delta_color="normal"):
    """
    Renderiza os cards superiores
    """
    with st.container(border=True):
        col1_metric, col2_icon = st.columns([2.5,1], vertical_alignment="top", gap="large")
        with col1_metric:
            st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
        with col2_icon:
            st.markdown(f"""
                <div class="icon-background {icon_bg_class}"> {icon_svg_string}
            """, unsafe_allow_html=True)

def render_setor_row_clickable(setor, itens, max_itens):
    """
    Renderiza a linha do setor
    """
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


def render_responsavel_row_clickable(sigla, avatar_class, nome, itens_text):
    """
    Renderiza a linha do responsável - ALINHAMENTO DE VERDADE AGORA
    """
    
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

# --- MAIN APP ---
if __name__ == "__main__":
    # Configs
    tabs = st.tabs(['Dashboard', 'BI & Análise'])
    st.set_page_config(page_title="IDF - Visão Analítica", layout="wide", page_icon="assets/logo.png")
    load_css("static/style.css")

    # Dataframe Init
    item_map = carregar_dados()
    df = pd.DataFrame.from_dict(item_map, orient="index").reset_index(drop=True)

    # Sidebar
    st.sidebar.header("Filtros")
    setores_sel = st.sidebar.multiselect("Selecione o Setor", options=df["SETOR"].unique())
    st.sidebar.divider()
    resp_sel = st.sidebar.multiselect("Selecione o Responsável", options=list(set(itertools.chain.from_iterable(df["RESPONSAVEL"]))))

    with tabs[0]: # Dashboard
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

        # --- Dados principais ---
        df_setores = get_data_setores()
        df_resp = get_data_responsaveis()

        df_setores_f = df_setores[df_setores["Setor"].isin(setores_sel)] if setores_sel else pd.DataFrame()
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
                        render_setor_row_clickable(row["Setor"], int(row["Itens"]), max_itens)

        # --- Responsáveis Ativos ---
        with col_resp:
            with st.container(border=True, height=300):
                st.subheader("Responsáveis Ativos")
                if df_resp_f.empty:
                    st.info("Selecione ao menos um responsável na barra lateral.")
                else:
                    for _, row in df_resp_f.iterrows():
                        render_responsavel_row_clickable(row["Sigla"], row["Avatar"], row["Nome"], row["Itens"])

        # --- Popups ---
        if "popup_setor" in st.session_state:
            setor_param, itens_val = st.session_state["popup_setor"]
            show_itens_setor(setor_param, itens_val)

        if "popup_resp" in st.session_state:
            resp_param, itens_text = st.session_state["popup_resp"]
            show_itens_responsavel(resp_param, itens_text)

    with tabs[1]:  # BI & Análise
        # -----------------------------
        #   CARREGAR DADOS
        # -----------------------------
        df2 = pd.read_csv("static/aleatorio.csv", sep=",")
        df_tab1 = pd.merge(df, df2, how="inner", on="ITEM")

        # -----------------------------
        #   NORMALIZAÇÃO RESPONSÁVEIS
        # -----------------------------
        def normalizar_responsavel(x):
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

        df_tab1["RESPONSAVEL"] = df_tab1["RESPONSAVEL"].apply(normalizar_responsavel)

        # -----------------------------
        #   LISTAS PARA FILTROS
        # -----------------------------
        df_base_aba = df_tab1.copy()

        if resp_sel:
            df_base_aba = df_base_aba[df_base_aba["RESPONSAVEL"].apply(
                lambda lista: any(resp in lista for resp in resp_sel)
            )]
        
        if setores_sel:
            df_base_aba = df_base_aba[df_base_aba["SETOR"].isin(setores_sel)]

        # -----------------------------
        #   2. FILTROS DA ABA (EM CASCATA)
        # -----------------------------
        with st.container(border=True, horizontal=True):
            
            # --- FILTRO DE STATUS ---
            # As opções de Status são baseadas no filtro da sidebar
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
            
            filtro_item = st.selectbox(
                "Item", 
                item_opcoes_dinamicas, # <-- Opções dinâmicas
                index=None, 
                placeholder="Item..."
            )

        # -----------------------------
        #   3. APLICAÇÃO FINAL DOS FILTROS
        # -----------------------------
        
        df_final = df_base_aba.copy()

        if filtro_status:
            df_final = df_final[df_final["STATUS"] == filtro_status]

        if filtro_item:
            df_final = df_final[df_final["ITEM"] == filtro_item]

        # -----------------------------
        #   DEBUG (LIGUE SE PRECISAR)
        # -----------------------------
        with st.expander("DEBUG"):
            st.subheader("⚙️ DEBUG - Responsáveis Normalizados")
            st.write(df_final[["ITEM", "RESPONSAVEL"]].head(25))
            st.write("Responsáveis selecionados:", resp_sel)

        # -----------------------------
        #   RENDERIZAÇÃO DE ITENS
        # -----------------------------
        for _, item in df_final.iterrows():
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
                                background-color:#EEF4FF;
                                color:#2563EB;
                                font-weight:600;
                                padding:16px 14px;
                                border-radius:8px;
                                font-size:0.9rem;
                                display:inline-block;
                            ">{item['ITEM']}</span>
                            """,
                            unsafe_allow_html=True
                        )

                    # --- equipe e status ---
                    with top_col2:
                        match item["SETOR"]:
                            case "SMS":
                                _color = "red"
                            case "QUALIDADE":
                                _color = "blue"
                            case "PRAZO":
                                _color = "orange"
                            case "GESTÃO":
                                _color = "green"
                        
                        match item["STATUS"]:
                            case "Concluido":
                                _color_hex = "#059669"
                                _icon_svg = """
                                fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd"
                                """
                            case "Em andamento":
                                _color_hex = "#d97706"
                                _icon_svg = """
                                fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm.75-13a.75.75 0 0 0-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 0 0 0-1.5h-3.25V5Z" clip-rule="evenodd"
                                """
                            case "Não enviado":
                                _color_hex = "#d91c1c"
                                _icon_svg = """
                                fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd" 
                                """

                        st.badge(item["SETOR"], color=_color)
                        st.markdown(
                            f"""
                            <div style="margin-top:-10px;">
                                <span style="
                                    color:{_color_hex};
                                    font-weight:500;
                                    font-size:0.9rem;
                                    display:inline-flex;
                                    align-items:center;
                                    gap:6px;
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
                            font-size:0.95rem;
                            color:#111827;
                            font-weight:500;
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
                            background-color:#E5E7EB;
                            height:6px;
                            width:100%;
                            border-radius:4px;
                            overflow:hidden;
                            margin-top:4px;
                        ">
                            <div style="
                                width:{item["PERCENTUAL"]}%;
                                height:100%;
                                background-color:#2563EB;
                            "></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # --- Expander ---
                with st.expander("Ver detalhes e documentos"):
                    st.write("📄 Aqui você pode colocar as evidências, anexos ou observações.")

            st.write("")