import streamlit as st
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


@st.cache_resource
def load_pages():

    pdf_path = Path(__file__).parent / "nodejs.pdf"

    loader = PyPDFLoader(str(pdf_path))

    return loader.load()


PAGES = load_pages()