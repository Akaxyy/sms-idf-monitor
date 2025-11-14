from streamlit_extras.pdf_viewer import pdf_viewer
import streamlit as st

if "mostrar_imagem" not in st.session_state:
    st.session_state.mostrar_imagem = False

def show_pdf():
    st.session_state.mostrar_imagem = not st.session_state.mostrar_imagem

st.button("Mostrar PDF", on_click=show_pdf)

if st.session_state.mostrar_imagem:
    pdf_viewer("assets/Documento_310725122457.pdf")