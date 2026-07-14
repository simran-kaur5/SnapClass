import streamlit as st

def footer_home():
    
    st.markdown("""
        <p style="margin-top:2rem; display:flex; justify-content:center; align-items:center;">
    <span style="color:#475569;">Made by</span>
    <span style="margin-left:6px; font-weight:900; font-size:18px;">
        Simranjit Kaur
    </span>
        </p>
                """
                , unsafe_allow_html=True)
