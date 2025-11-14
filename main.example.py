import streamlit as st
import pandas as pd
from static.svg_icons import * # seus ícones SVG

# --- FUNÇÕES UTILITÁRIAS ---
def load_css(file_path):
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo CSS não encontrado: {file_path}")

# --- POPUP: Itens por Setor ---
@st.dialog("📊 Detalhes do Setor")
def show_itens_setor(setor, itens):
    st.write(f"### {setor}")
    st.write("Itens relacionados:")

    for i in range(1, itens + 1):
        st.markdown(f"- Item {i} do setor {setor}")
    
    # ATUALIZADO: Fecha limpando o session_state
    if st.button("Fechar"):
        st.session_state.pop("popup_setor", None)

# --- POPUP: Itens por Responsável ---
@st.dialog("👤 Itens do Responsável")
def show_itens_responsavel(nome, itens_text):
    st.write(f"### {nome}")
    st.write("Itens atribuídos:")

    try:
        count = int(str(itens_text).split()[0])
    except Exception:
        count = 0
        
    if count == 0:
        st.write("Nenhum item atribuído.")
        
    for i in range(1, count + 1):
        st.markdown(f"- Item {i} de {nome}")
        
    # ATUALIZADO: Fecha limpando o session_state
    if st.button("Fechar"):
        st.session_state.pop("popup_resp", None)

# --- COMPONENTES VISUAIS ---
# (render_metric_card permanece o mesmo)
def render_metric_card(label, value, delta, icon_svg_string, icon_bg_class, delta_color="normal"):
    with st.container(border=True):
        col1_metric, col2_icon = st.columns([2.5,1], vertical_alignment="top", gap="large")
        with col1_metric:
            st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
        with col2_icon:
            st.markdown(f"""
                <div class="icon-background {icon_bg_class}">
                    {icon_svg_string}
            """, unsafe_allow_html=True)

# As funções render_..._clickable foram removidas, 
# pois o layout será feito direto no loop principal.

# --- MAIN APP ---
if __name__ == "__main__":
    st.set_page_config(page_title="IDF - Visão Analítica", layout="wide", page_icon="assets/logo.png")
    load_css("static/style.css")

    st.sidebar.header("Filtros")
    x = st.sidebar.multiselect("Selecione o Setor", options=["SMS", "QUALIDADE", "PRAZO", "GESTÃO"])
    st.sidebar.divider()
    y = st.sidebar.multiselect("Selecione o Responsável", options=["Leonardo/Nathalia", "Alex", "Tadeu", "João"])

    st.title("Dashboard de Análise - IDF")
    st.write("##### Visão geral dos itens de análise e documentação")
    st.divider()

    # --- MÉTRICAS ---
    with st.container():
        col1, col2, col3, col4 = st.columns([2.5, 2.5, 2.5, 2.5])
        with col1:
            render_metric_card("Total de Itens", "24", "+2 (últ. dia)", ICON_ITENS, "icon-bg-blue")
        with col2:
            render_metric_card("Pendentes", "6", "-1 (últ. dia)", ICON_PENDENTES, "icon-bg-orange")
        with col3:
            render_metric_card("Concluídos", "16", "0.1%", ICON_CONCLUSAO, "icon-bg-green")
        with col4:
            render_metric_card("Taxa de Conclusão", "67%", "+3 (últ. dia)", ICON_TAXA, "icon-bg-cyan")

    # --- PAINÉIS ---
    col_setor, col_resp = st.columns(2)

    # Dados
    data_setor = {"Setor": ["SMS", "QUALIDADE", "PRAZO", "GESTÃO"], "Itens": [2, 7, 1, 1]}
    df_data_setor = pd.DataFrame(data_setor)
    df_data_setor_filter = df_data_setor[df_data_setor["Setor"].isin(x)] if x else pd.DataFrame(columns=df_data_setor.columns)

    with col_setor:
        with st.container(border=True, height=280):
            st.subheader("Itens por Setor")

            if df_data_setor_filter.empty:
                st.info("Selecione ao menos um setor na barra lateral.")
            else:
                max_itens = df_data_setor_filter["Itens"].max()
                
                # ATUALIZADO: Loop refeito com colunas e botão
                for _, row in df_data_setor_filter.iterrows():
                    setor = row["Setor"]
                    itens = int(row["Itens"])
                    percent = int((itens / max_itens) * 100) if max_itens > 0 else 0
                    
                    col_bar_display, col_button_action = st.columns([4, 1.2])
                    
                    with col_bar_display:
                        # HTML para a barra (sem o link <a>)
                        html = f"""
                        <div class="setor-row"> 
                            <div class="setor-label">{setor}</div>
                            <div class="setor-bar-container">
                                <div class="setor-bar" style="width: {percent}%;"></div>
                            </div>
                            <div class="setor-value">{itens}</div>
                        </div>
                        """
                        st.markdown(html, unsafe_allow_html=True)
                        
                    with col_button_action:
                        # Botão que define o session_state
                        if st.button("Detalhes", key=f"setor_{setor}", use_container_width=True):
                            st.session_state["popup_setor"] = (setor, itens)

    # Responsáveis
    data_resp = {
        "Sigla": ["LE", "AL", "TA", "JO"],
        "Avatar": ["avatar-le", "avatar-al", "avatar-ta", "avatar-jo"],
        "Nome": ["Leonardo/Nathalia", "Alex", "Tadeu", "João"],
        "Itens": ["3 itens", "5 itens", "1 item", "3 itens"],
    }
    df_resp = pd.DataFrame(data_resp)
    df_resp_filter = df_resp[df_resp["Nome"].isin(y)] if y else pd.DataFrame(columns=df_resp.columns)

    with col_resp:
        with st.container(border=True, height=280):
            st.subheader("Responsáveis Ativos")
            if df_resp_filter.empty:
                st.info("Selecione ao menos um responsável na barra lateral.")
            else:
                # ATUALIZADO: Loop refeito com colunas e botão (como no seu exemplo)
                for _, row in df_resp_filter.iterrows():
                    col_avatar, col_nome, col_btn = st.columns([0.6, 2, 1.2])
                    
                    with col_avatar:
                        # Recriando o avatar (baseado no seu CSS/HTML anterior)
                        st.markdown(f'<div class="avatar {row["Avatar"]}" style="width:35px; height:35px;">{row["Sigla"]}</div>', unsafe_allow_html=True)
                    
                    with col_nome:
                        st.write(row["Nome"]) # O CSS .responsavel-nome deve pegar isso
                        
                    with col_btn:
                        # Botão que define o session_state
                        if st.button(row["Itens"], key=f"resp_{row['Nome']}", use_container_width=True):
                            st.session_state["popup_resp"] = (row["Nome"], row["Itens"])

    # --- ATUALIZADO: Lê o session_state e abre o popup correspondente ---
    
    if "popup_setor" in st.session_state:
        setor_param, itens_val = st.session_state["popup_setor"]
        show_itens_setor(setor_param, itens_val)

    if "popup_resp" in st.session_state:
        resp_param, itens_text = st.session_state["popup_resp"]
        show_itens_responsavel(resp_param, itens_text)
