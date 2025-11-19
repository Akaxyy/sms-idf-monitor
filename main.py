import itertools
from os import replace
import pandas as pd
import json
import requests
from datetime import datetime
from pathlib import Path
from os import getlogin
import streamlit as st
from streamlit_extras.pdf_viewer import pdf_viewer


from static.svg_icons import *

from src.utils import normalizar_responsavel, limpar_id_item
from src.ui_components import render_css
from src.data_service import processar_merge_api

# =============================================================================
BASE_PATH = Path(fr"C:/Users/{getlogin()}/C3 ENGENHARIA/C3 Engenharia SEDE - 3.1.30 - IDF")

API_URL = "http://localhost:8000/sms?month="

MONTH_OPTIONS = {
    "Março": "3.%20Março",
    "Abril": "04.%20Abril",
    "Maio": "05.%20Maio",
    "Junho": "06.%20Junho",
    "Julho": "07.%20Julho",
    "Agosto": "08.%20Agosto",
    "Setembro": "09.%20Setembro",
    "Outubro": "10.%20Outubro",
    "Novembro": "11.%20Novembro",
    "Dezembro": "12.%Dezembro"
}

# =============================================================================
# 1. FUNÇÕES DE CARREGAMENTO DE DADOS E CONFIGURAÇÃO
# =============================================================================

@st.cache_data
def carregar_dados_principais():
    """Carrega dados do JSON."""
    try:
        with open("./static/data.json", 'r', encoding="utf-8") as f:
            item_map = json.load(f)
        df = pd.DataFrame.from_dict(item_map, orient="index").reset_index(drop=True)
        if not df.empty:
            df["RESPONSAVEL"] = df["RESPONSAVEL"].apply(normalizar_responsavel)
            df["ITEM"] = df["ITEM"].apply(limpar_id_item)
        return df

    except Exception as e:
        st.error(f"Erro ao carregar data.json: {e}")
        return pd.DataFrame()

# =============================================================================
# 2. COMPONENTES DE UI (POPUPS / DIALOGS)
# =============================================================================

def _buscar_detalhes_do_item_na_api(item_codigo):
    """
    Busca os detalhes completos de um item na API armazenada no session_state.
    VERSÃO CORRIGIDA - Adiciona tratamento de erros robusto.
    """
    try:
        api_data = st.session_state.get('api_response', {})
        
        # Verifica se existe a estrutura esperada
        if not api_data:
            return None
        
        # Navega para o segundo 'result' (se existir)
        if isinstance(api_data, dict):
            itens_por_setor = api_data.get('result', api_data)
        else:
            itens_por_setor = api_data
        
        # Itera sobre todos os setores para encontrar o item
        if isinstance(itens_por_setor, dict):
            for setor_nome, itens in itens_por_setor.items():
                if isinstance(itens, dict):
                    detalhes = itens.get(item_codigo)
                    if detalhes:
                        return detalhes
        return None
        
    except Exception as e:
        st.warning(f"Erro ao buscar detalhes do item {item_codigo}: {e}")
        return None

def _render_pendencias_detalhadas(df_pendencias):
    """
    Renderiza as pendências detalhadas com diretórios faltantes.
    VERSÃO CORRIGIDA - Agora verifica se há pelo menos um item para exibir.
    """
    
    if df_pendencias.empty:
        st.success("🎉 Nenhuma pendência encontrada para os itens filtrados!")
        return
    
    # Flag para saber se encontramos algo para exibir
    encontrou_pendencia_diretorio = False
    
    for _, item in df_pendencias.iterrows():
        item_codigo = item['ITEM']
        
        # 1. Busca os detalhes originais da API
        detalhes_api = _buscar_detalhes_do_item_na_api(item_codigo)
        
        # 2. Filtra os diretórios pendentes (qtd: 0)
        if detalhes_api and detalhes_api.get('diretorios'):
            diretorios_pendentes = [
                dir_info for dir_info in detalhes_api['diretorios'] 
                if dir_info.get("qtd", 0) == 0
            ]
            
            # 3. Só exibe se houver diretórios pendentes
            if diretorios_pendentes:
                encontrou_pendencia_diretorio = True
                
                st.markdown(f"#### 📄 Item {item_codigo} ({item['SETOR']})")
                
                # Formata lista de responsáveis
                responsaveis = item.get('RESPONSAVEL', [])
                if isinstance(responsaveis, list):
                    resp_str = ', '.join(responsaveis)
                else:
                    resp_str = str(responsaveis)
                
                st.markdown(f"**Status:** {item['STATUS']} | **Responsáveis:** {resp_str}")
                
                with st.container(border=True):
                    st.markdown("##### 📁 **Diretórios Pendentes (Qtd: 0)**")
                    for dir_info in diretorios_pendentes:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;- `{dir_info['diretorio']}`")
                
                st.divider()
    
    # 4. Mensagem final
    if not encontrou_pendencia_diretorio:
        st.success("🎉 Todos os diretórios possuem arquivos! Nenhuma pendência encontrada.")

def construir_caminho_arquivo(diretorio_relativo, arquivo, setor, mes):
    """
    Constrói o caminho completo do arquivo usando o path da API.
    
    Args:
        diretorio_relativo: Ex: "3. Gestão de SMS/3.2 Avaliações..."
        arquivo: Ex: "PCMSO LV CASTRO Rev. 5.PDF"
        setor: Ex: "SMS"
    """
    import os
    
    # Pega o path base da API
    mes_ajustado = MONTH_OPTIONS[mes].replace("%20", " ")
    path_base = f"{BASE_PATH}/{mes_ajustado}"
    
    # Mapeia o setor para a pasta correta
    setor_mapping = {
        "SMS": "1. SMS",
        "QUALIDADE": "2. Qualidade",
        "PRAZO": "3. Prazo",
        "GESTÃO": "4. Gestão"
    }
    
    setor_pasta = setor_mapping.get(setor, setor)
    
    # Remove barras iniciais do diretório relativo
    diretorio_limpo = diretorio_relativo.lstrip("/\\")
    
    # Constrói o caminho completo
    caminho_completo = os.path.join(
        path_base,    
        setor_pasta, 
        diretorio_limpo,  
        arquivo  
    )
    
    return caminho_completo.replace("/", "\\")

if "show_pdf" not in st.session_state:
    st.session_state.show_pdf = False
if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = False


@st.dialog("Detalhes do Setor", width="medium")
def show_itens_setor(df_completo, setor):
    """Mostra pendências detalhadas de um setor específico."""
    st.write(f"### Pendências do Setor: {setor}")
    
    # 1. Filtra por Setor e por Status (Apenas itens não concluídos)
    df_setor = df_completo[df_completo['SETOR'] == setor].copy()
    df_pendencias = df_setor[
        ~df_setor['STATUS'].astype(str).str.contains("Concluído|Concluido", case=False, na=False)
    ]
    
    # 2. Renderiza as pendências
    if df_pendencias.empty:
        st.success("🎉 Nenhuma pendência encontrada para este setor!")
    else:
        _render_pendencias_detalhadas(df_pendencias)
    
    # 3. Botão de fechar
    if st.button("Fechar", key=f"close_setor_{setor}", use_container_width=True, type="primary"):
        st.rerun()

@st.dialog("Itens do Responsável", width="medium")
def show_itens_responsavel(df_completo, nome):
    """Mostra pendências detalhadas de um responsável específico."""
    st.write(f"### Pendências de: {nome}")
    
    # 1. Explode o DataFrame e filtra pelo nome do responsável
    df_exploded = df_completo.explode('RESPONSAVEL')
    df_resp = df_exploded[df_exploded['RESPONSAVEL'] == nome].copy()
    
    # 2. Filtra apenas itens não concluídos
    df_pendencias = df_resp[
        ~df_resp['STATUS'].astype(str).str.contains("Concluído|Concluido", case=False, na=False)
    ]
    
    # 3. Renderiza as pendências
    if df_pendencias.empty:
        st.success("🎉 Nenhuma pendência encontrada para este responsável!")
    else:
        _render_pendencias_detalhadas(df_pendencias)
    
    # 4. Botão de fechar
    if st.button("Fechar", key=f"close_resp_{nome}", use_container_width=True, type="primary"):
        st.rerun()

@st.dialog("Visualizador de PDF", width="large", on_dismiss="rerun")
def show_pdf_popup(file):
    """Exibe o PDF em um modal popup"""
    
    # Verifica se o arquivo existe antes de tentar abrir
    import os
    if not file or not os.path.exists(file):
        st.error(f"Arquivo não encontrado: {file}")
        if st.button("Voltar"):
            st.session_state.show_pdf = False
            st.session_state.pdf_file = None
            st.rerun()
        return

    if st.button("Fechar PDF", key="close_pdf_popup", use_container_width=True, type="primary"):
        # Limpa o estado para não reabrir o modal no próximo refresh
        st.session_state.show_pdf = False
        st.session_state.pdf_file = None
        st.rerun()
        
        
    pdf_viewer(file)

@st.dialog("Arquivos do Diretório")
def show_itens_bi(arquivos_list, diretorio, setor, mes):
    """Mostra a lista de arquivos de um diretório específico."""
    st.write(f"### Arquivos Encontrados ({len(arquivos_list)} itens)")
    
    if not arquivos_list:
        st.info("Nenhum arquivo encontrado neste diretório.")
    else:
        # Renderiza cada arquivo
        for idx, arquivo in enumerate(arquivos_list, 1):
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    st.markdown(f"**#{idx}**")
                with col2:
                    st.markdown(f"📄 `{arquivo}`")
                    
                with col3:
                    if arquivo.lower().endswith(".pdf"):
                        btn_key = f"view_pdf_{idx}_{arquivo[:10]}"
                        if st.button("👁️", key=btn_key):
                            caminho_completo = construir_caminho_arquivo(
                                diretorio, arquivo, setor, mes
                            )
                            print(caminho_completo)
                            st.session_state.pdf_file = caminho_completo
                            st.session_state.show_pdf = True
                            st.rerun()

                            

    # Botão de fechar
    if st.button("Fechar", key="close_arquivos", use_container_width=True, type="primary"):
        st.rerun()

# =============================================================================
# 3. COMPONENTES DE UI (WIDGETS REUTILIZÁVEIS)
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

def render_setor_row(df_completo, setor, itens, max_itens):
    """
    Renderiza a linha do setor com botão que abre o popup.
    VERSÃO CORRIGIDA - Garante que o dataframe completo seja passado.
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
        # CORREÇÃO: Usa um identificador único e estável
        if st.button(f"{itens}", key=f"btn_setor_{setor}_{itens}", type="secondary"):
            show_itens_setor(df_completo, setor)

def render_responsavel_row(df_completo, sigla, avatar_class, nome, itens_text):
    """
    Renderiza a linha do responsável com botão que abre o popup.
    VERSÃO CORRIGIDA - Garante que o dataframe completo seja passado.
    """
    col_html, col_btn = st.columns([3, 1], vertical_alignment="center") 

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
        # CORREÇÃO: Usa um identificador único e estável
        if st.button(f"{itens_text}", key=f"btn_resp_{nome.replace(' ', '_')}", type="secondary"):
            show_itens_responsavel(df_completo, nome)


def render_bi_item(item_row, mes_sel):
    """Renderiza um único card de item na aba BI & Análise."""
    item = item_row 
    
    with st.container(border=True):
        col1, col2 = st.columns([9, 1], vertical_alignment="top")

        # ======================
        # COLUNA ESQUERDA
        # ======================
        with col1:
            top_col1, top_col2 = st.columns([1, 13], vertical_alignment="top")

            with top_col1:
                st.markdown(
                    f"""
                    <span style="
                        background-color:#EEF4FF; color:#2563EB; font-weight:600;
                        padding:16px 14px; border-radius:8px; font-size:0.8rem;
                        display:inline-block;
                    ">{item['ITEM']}</span>
                    """,
                    unsafe_allow_html=True
                )

            with top_col2:
                match item["SETOR"]:
                    case "SMS": _color = "red"
                    case "QUALIDADE": _color = "blue"
                    case "PRAZO": _color = "orange"
                    case "GESTÃO": _color = "green"
                    case _: _color = "gray"
                
                item_status = str(item.get("STATUS", "N/A"))

                match item_status:
                    case "Concluído":
                        _color_hex = "#059669"
                        _icon_svg = 'fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd"'
                    case "Em Andamento":
                        _color_hex = "#d97706"
                        _icon_svg = 'fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm.75-13a.75.75 0 0 0-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 0 0 0-1.5h-3.25V5Z" clip-rule="evenodd"'
                    case "Não Iniciado":
                        _color_hex = "#d91c1c"
                        _icon_svg = 'fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd"'
                    case _: # Inclui "N/A"
                        _color_hex = "#555"
                        _icon_svg = "" 

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
                            {item_status}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                avatars = ""
                offset = 0

                for user in item["RESPONSAVEL"]:
                    initials = user[0:2].upper()
                    
                    avatars += f"""
                        <div title="{user}" style="
                            width: 28px;
                            height: 28px;
                            background: #CCCCCC;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: 600;
                            font-size: 12px;
                            color: #333;
                            text-transform: uppercase;
                            position: relative;
                            left: {-offset}px;
                            border: 2px solid white;
                            cursor: help; /* Muda o mouse para indicar que tem info */
                        ">{initials}</div>
                    """
                    offset += 8

                st.html(
                f"""
                <div style="
                    display: flex;
                    align-items: center;
                    margin-bottom: 8px;
                    position: relative;
                    height: 30px;
                ">
                    {avatars}
                </div>
                """,
            )


        # ======================
        # COLUNA DIREITA
        # ======================
        with col2:
            try:
                percentual_val = int(item.get("PERCENTUAL", 0))
            except (ValueError, TypeError):
                percentual_val = 0
                
            st.markdown(
                f"""
                <div style="text-align:right; font-size:1.5rem; font-weight:700; color:#111827;">
                    {percentual_val}%
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div style="
                    background-color:#E5E7EB; height:6px; width:100%;
                    border-radius:4px; overflow:hidden; margin-top:4px;
                ">
                    <div style="
                        width:{percentual_val}%; height:100%;
                        background-color:#2563EB;
                    "></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # --- INÍCIO DA ALTERAÇÃO ---
        with st.expander("Ver detalhes e documentos"):
            
            # Pega a lista de diretorios
            diretorios_list = item.get("DIRETORIOS", [])
            
            if not diretorios_list:
                st.info("Nenhum diretório ou evidência registrada para este item.")
            else:
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.info(f"**Responsáveis:**\n\n{', '.join(item['RESPONSAVEL'])}", icon="👥")

                with c2:
                    month = int(MONTH_OPTIONS[mes_sel][0:2])
                    date_diff = (datetime.today().replace(day=27, month=month) - datetime.today()).days
            
                    if date_diff <= 0: st.success("**Prazo**\n\nPeríodo finalizado",  icon="✅")
                    elif date_diff <= 7: st.error(f"**Prazo**\n\nFaltam {date_diff} dias",  icon="📅")
                    elif date_diff >= 20: st.info(f"**Prazo**\n\nFaltam {date_diff} dias",  icon="📅")
                    elif date_diff >= 7: st.warning(f"**Prazo**\n\nFaltam {date_diff} dias",  icon="📅")

                with c3:
                    st.info(f"**Previsão:**\n\n{int(item['PREVISAO'])} Itens", icon="📄")

                with st.container(border=True):
                    for dir_info in diretorios_list:
                        dir_path = dir_info.get("diretorio", "N/A")
                        dir_qtd = dir_info.get("qtd", 0)
                        dir_files = dir_info.get("itens", [])
                        
                        col_path, col_qtd = st.columns([5, 1])
                        
                        with col_path:
                            st.markdown(f"📁 `{dir_path}`")
                        
                        with col_qtd:
                            if dir_qtd == 0:
                                st.badge(f"{dir_qtd} arquivos", color="gray")
                            else:
                                btn_key = f"btn_dir_{item['ITEM']}_{dir_path.replace('/', '_').replace('\\', '_')}"
                                if st.button(f"{dir_qtd} arquivos", key=btn_key, type='primary'):
                                    show_itens_bi(dir_files, dir_path, item["SETOR"], mes_sel)
        st.write("")

# =============================================================================
# 4. RENDERIZAÇÃO DAS PÁGINAS PRINCIPAIS (VIEWS)
# =============================================================================

def render_sidebar(df: pd.DataFrame):
    """Renderiza a barra lateral e retorna as seleções."""
    st.sidebar.header("Filtros")
    
    # df["SETOR"] deve vir do data.json
    setores_opcoes = df["SETOR"].unique()
    setores_sel = st.sidebar.multiselect("Selecione o Setor", options=setores_opcoes, placeholder="Selecione o Setor")
    
    # df["RESPONSAVEL"] já deve estar normalizado aqui
    responsaveis_opcoes = list(set(itertools.chain.from_iterable(df["RESPONSAVEL"])))
    resp_sel = st.sidebar.multiselect("Selecione o Responsável", options=sorted(responsaveis_opcoes), placeholder="Selecione o Responsável")

    mes_opcoes = ["Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    

    default_index = 8 # Default para Novembro (índice 8)
    try:
        # Tenta pegar o mês atual (ex: 11) e subtrair 3
        current_month_index = int(datetime.now().strftime("%m")) - 3
        if 0 <= current_month_index < len(mes_opcoes):
             default_index = current_month_index
    except Exception:
        pass # Mantém o fallback (Novembro)

    mes_sel = st.sidebar.selectbox("Mês", mes_opcoes, index=default_index)
    
    return setores_sel, resp_sel, mes_sel

def render_dashboard_tab(df_completo, setores_sel, resp_sel, mes_sel):
    """Renderiza o Dashboard com contagem real de itens pendentes por usuário."""
    
    st.title(f"Dashboard de Análise - {mes_sel}") # Opcional: Adicionei o mês no título para feedback visual
    st.divider()

    # --- 1. APLICAR FILTROS DA SIDEBAR (Setor e Responsável) ---
    df_dash = df_completo.copy()

    if setores_sel:
        df_dash = df_dash[df_dash["SETOR"].isin(setores_sel)]
    
    if resp_sel:
        df_dash = df_dash[df_dash["RESPONSAVEL"].apply(
            lambda lista: any(resp in lista for resp in resp_sel)
        )]

    # --- 2. CÁLCULO DAS MÉTRICAS GERAIS ---
    total_itens = len(df_dash)
    
    if "STATUS" in df_dash.columns:
        status_series = df_dash["STATUS"].fillna("Não Iniciado").astype(str).str.lower()
    else:
        status_series = pd.Series(["não iniciado"] * total_itens)

    qtd_concluido = status_series[status_series.str.contains("concluído|concluido")].count()
    qtd_andamento = status_series[status_series.str.contains("em andamento|execução")].count()
    qtd_nao_iniciado = status_series[status_series.str.contains("não iniciado|não enviado")].count()

    taxa_conclusao = (qtd_concluido / total_itens * 100) if total_itens > 0 else 0

    # --- 3. RENDERIZAÇÃO DOS CARDS ---
    with st.container():
        c1, c2, c3, c4 = st.columns(4)
        with c1: render_metric_card("Em Execução", f"{qtd_andamento}", None, ICON_ITENS, "icon-bg-blue")
        with c2: render_metric_card("Não Iniciado", f"{qtd_nao_iniciado}", None, ICON_PENDENTES, "icon-bg-orange")
        with c3: render_metric_card("Concluídos", f"{qtd_concluido}", None, ICON_CONCLUSAO, "icon-bg-green")
        with c4: render_metric_card("Taxa Conclusão", f"{taxa_conclusao:.1f}%", None, ICON_TAXA, "icon-bg-cyan")

    # --- 4. GRÁFICOS E LISTAS ---
    col_setor, col_resp = st.columns(2)

    # --- A. Itens Faltantes por Setor (CORRIGIDO) ---
    with col_setor:
        with st.container(border=True, height=400):
            st.subheader("Itens Faltantes por Setor")
            
            # --- CORREÇÃO AQUI ---
            # Cria um DF temporário apenas com o que NÃO está concluído
            df_faltantes = df_dash[
                ~df_dash['STATUS'].astype(str).str.contains("Concluído|Concluido", case=False, na=False)
            ]
            
            if df_faltantes.empty:
                 # Se tudo estiver concluído ou não houver dados filtrados
                if df_dash.empty:
                    st.info("Sem dados para os filtros selecionados.")
                else:
                    st.success("Todos os itens foram concluídos neste mês!")
            else:
                # Conta apenas os itens desse DF filtrado (Faltantes)
                df_setores_view = df_faltantes["SETOR"].value_counts().reset_index()
                df_setores_view.columns = ["Setor", "Itens"]
                
                max_itens = df_setores_view["Itens"].max()
                
                for _, row in df_setores_view.iterrows():
                    # Passamos df_faltantes aqui para que o popup abra os itens certos
                    render_setor_row(df_faltantes, row["Setor"], int(row["Itens"]), int(max_itens))

    # --- B. Itens Pendentes por Responsável ---
    with col_resp:
        with st.container(border=True, height=400):
            st.subheader("Pendências por Responsável")
            
            if df_dash.empty:
                st.info("Sem dados.")
            else:
                df_exploded = df_dash.explode('RESPONSAVEL')

                # Filtra apenas o que NÃO está concluído
                df_pendentes = df_exploded[
                    ~df_exploded['STATUS'].astype(str).str.contains("Concluído|Concluido", case=False, na=False)
                ]

                if df_pendentes.empty:
                    st.success("Nenhuma pendência encontrada para os filtros atuais!")
                else:
                    contagem_resp = df_pendentes['RESPONSAVEL'].value_counts().reset_index()
                    contagem_resp.columns = ['Nome', 'Qtd_Pendentes']
                    
                    for _, row in contagem_resp.iterrows():
                        nome = row['Nome']
                        qtd = row['Qtd_Pendentes']
                        sigla = nome[:2].upper() if isinstance(nome, str) else "??"
                        avatar_class = "avatar-ta" if qtd < 3 else "avatar-le" 
                        item_text = f"{qtd} pendentes"
                        
                        render_responsavel_row(df_dash, sigla, avatar_class, nome, item_text)        


def render_bi_tab(df_base_normalizada, setores_sel, resp_sel, mes_sel):
    """Renderiza todo o conteúdo da aba 'BI & Análise'."""
    
    if df_base_normalizada.empty:
        st.error("Dados de BI não puderam ser carregados. Verifique o arquivo data.json.")
        return

    # -----------------------------
    # 1. FILTRAGEM DA SIDEBAR
    # -----------------------------
    df_base_aba = df_base_normalizada.copy()

    if resp_sel:
        # Filtra o dataframe se a lista 'RESPONSAVEL' contiver QUALQUER um dos responsáveis selecionados
        df_base_aba = df_base_aba[df_base_aba["RESPONSAVEL"].apply(
            lambda lista: any(resp in lista for resp in resp_sel)
        )]
    
    if setores_sel:
        df_base_aba = df_base_aba[df_base_aba["SETOR"].isin(setores_sel)]

    # -----------------------------
    # 2. FILTROS DA ABA (EM CASCATA)
    # -----------------------------
    with st.container(border=True):
        filter_cols = st.columns(2)
        
        with filter_cols[0]:
            # Pega opções de status do DF já mesclado, tratando Nulos
            status_opcoes = sorted(df_base_aba["STATUS"].dropna().unique())
            filtro_status = st.selectbox(
                "Status", status_opcoes, index=None, placeholder="Status..."
            )

        df_para_itens = df_base_aba[df_base_aba["STATUS"] == filtro_status] if filtro_status else df_base_aba
        
        with filter_cols[1]:
            item_opcoes_dinamicas = sorted(df_para_itens["ITEM"].dropna().unique())
            filtro_item = st.selectbox(
                "Item", item_opcoes_dinamicas, index=None, placeholder="Item..."
            )

    # -----------------------------
    # 3. APLICAÇÃO FINAL DOS FILTROS
    # -----------------------------
    df_final = df_base_aba.copy()
    if filtro_status:
        df_final = df_final[df_final["STATUS"] == filtro_status]
    if filtro_item:
        df_final = df_final[df_final["ITEM"] == filtro_item]

    # 4. DEBUG
    with st.expander("DEBUG"):
        st.subheader("⚙️ DEBUG - Dados Pós-Merge e Pós-Filtro")
        st.write(st.session_state)
        st.write(st.session_state.show_pdf)
        st.write(st.session_state.pdf_file)
        st.write("Filtros da Sidebar:", {"Setores": setores_sel, "Responsáveis": resp_sel, "Mês": mes_sel})
        st.write("Filtros da Aba:", {"Status": filtro_status, "Item": filtro_item})
        st.write(df_final[["ITEM", "RESPONSAVEL", "SETOR", "STATUS", "PERCENTUAL"]].head(25))

    # 5. RENDERIZAÇÃO DE ITENS
    if df_final.empty:
        st.info("Nenhum item encontrado com os filtros selecionados.")
    else:
        for _, item in df_final.iterrows():
            render_bi_item(item, mes_sel)

# =============================================================================
# 7. LÓGICA DE API (MOVIDA PARA O ESCOPO PRINCIPAL)
# =============================================================================

@st.fragment(run_every=30)
def fetch_api_fragment(mes_selecionado):
    """
    Busca dados da API e armazena em st.session_state.api_response.
    Esta função agora é chamada de dentro de main() para rodar sempre.
    """
    if 'api_response' not in st.session_state:
        st.session_state.api_response = {}
        
    try:
        # mes_selecionado vem da sidebar
        if mes_selecionado not in MONTH_OPTIONS:
            # Não mostra toast se for a primeira execução
            if "sidebar_mes_sel" in st.session_state: 
                st.toast(f"Mês '{mes_selecionado}' inválido para API.", icon="⚠️")
            return # Retorna silenciosamente se o mês for inválido

        api_month_value = MONTH_OPTIONS[mes_selecionado]
        
        response = requests.get(API_URL + api_month_value)
        response.raise_for_status()
        new_data = response.json().get("result", {}) 

        old_data = st.session_state.api_response

        if new_data != old_data:
            st.session_state.api_response = new_data
            st.rerun()

    except requests.exceptions.RequestException as e:
        st.toast(f"Erro ao conectar na API: {e}", icon="🔥")
    except Exception as e:
        st.toast(f"Erro ao processar dados da API no fragment: {e}", icon="⚠️")

# =============================================================================
# 8. APLICAÇÃO PRINCIPAL (MAIN)
# =============================================================================

def main():
    """Função principal que executa o app Streamlit."""
    
    # --- Configurações Iniciais ---
    st.set_page_config(page_title="IDF - Visão Analítica", layout="wide", page_icon="assets/logo.png")
    render_css("static/style.css")

    if st.session_state.show_pdf and st.session_state.pdf_file:
        show_pdf_popup(st.session_state.pdf_file)

    # --- Carregamento e Preparação de Dados Estáticos ---
    df_principal = carregar_dados_principais()

    # --- Normaliza os responsaveis --- 
    df_principal["RESPONSAVEL"] = df_principal["RESPONSAVEL"].apply(normalizar_responsavel)

    # --- Renderização da Sidebar ---
    setores_sel, resp_sel, mes_sel = render_sidebar(df_principal)

    # --- Fragmento de Busca de Dados (ATUALIZA o st.session_state.api_response) ---
    fetch_api_fragment(mes_sel)

    # --- Junção de Dados Dinâmicos ---
    # Pega os dados mais recentes da API (do session_state)
    api_data = st.session_state.get('api_response', {})
    
    # Chama sua função para mesclar os dados estáticos com os da API
    df_finalziado = processar_merge_api(df_principal, api_data)

    # --- Renderização das Abas ---
    tabs = st.tabs(['Dashboard', 'BI & Análise'])
    
    with tabs[0]:
        render_dashboard_tab(df_finalziado, setores_sel, resp_sel, mes_sel)
        
    with tabs[1]:
        render_bi_tab(df_finalziado, setores_sel, resp_sel, mes_sel)

if __name__ == "__main__":
    main()
