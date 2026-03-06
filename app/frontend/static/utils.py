import os
import streamlit as st

def inject_css(filename: str):
    """Injects custom CSS from a file into the Streamlit app."""
    style_path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(style_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ Style file '{filename}' not found.")
