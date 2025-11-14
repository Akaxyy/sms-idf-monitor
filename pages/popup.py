import streamlit as st

st.set_page_config(layout="wide")
st.write(st.session_state)

# --- Função de popup (dialog) ---
@st.dialog("Itens do Responsável")
def show_itens(nome, itens):
    st.write(f"### {nome}")
    for item in itens:
        st.markdown(f"- {item}")
    st.button("Fechar", on_click=lambda: st.session_state.pop("show_popup", None))

# --- Dados base ---
responsaveis = [
    {"sigla": "AL", "nome": "Alex", "itens": ["Tubo danificado", "Parafuso solto", "Fita isolante", "Relatório pendente", "EPIs"]},
    {"sigla": "LE", "nome": "Leonardo/Nathalia", "itens": ["Checklist A", "Inspeção B", "Envio C"]},
]

# --- Renderiza cada linha ---
for r in responsaveis:
    col1, col2, col3 = st.columns([0.5, 2, 1])
    with col1:
        st.markdown(f"<div style='background:#DFFFE3;border-radius:50%;width:35px;height:35px;display:flex;align-items:center;justify-content:center;font-weight:bold'>{r['sigla']}</div>", unsafe_allow_html=True)
    with col2:
        st.write(r["nome"])
    with col3:
        if st.button(f"{len(r['itens'])} itens", key=r["sigla"]):
            st.session_state["show_popup"] = (r["nome"], r["itens"])

# --- Exibe popup se solicitado ---
if "show_popup" in st.session_state:
    nome, itens = st.session_state["show_popup"]
    show_itens(nome, itens)
