# src/ui_components.py
import streamlit as st
from static.svg_icons import *

def render_css(file_path):
    """Carrega um arquivo CSS"""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS não encontrado: {file_path}")