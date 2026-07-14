import streamlit as st

def home_background():

    st.markdown("""

        <style>
                .stApp{
                    background: linear-gradient(
                        135deg,
                        #E8F0FF,
                        #C9D8FF,
                        #D9CCFF
                    );
                }

                .stApp div[data-testid="stColumn"] > div{
                    background-color: #DCE8FF  !important;
                    padding:2.5rem !important;
                    border-radius:5rem !important;
                }
                </style>
                """,unsafe_allow_html=True)
    
def dashboard_background():
    st.markdown("""

        <style>
                .stApp{
                    background:#E0E3FF !important;
                }
                </style>
                """,unsafe_allow_html=True)
    
def base_style():

    st.markdown("""
                <style>
                    
                </style>
                
        <style>
                @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
                /* hide top bar of streamlit app */
                #MainMenu,header,footer{
                    visibility:hidden !important;
                }

                
                .block-container {
                    padding-top: 0rem !important;    
                }

                h1{
                    font-family: 'Sora', sans-serif !important;
                    font-size: 4.5rem !important;
                    margin-bottom:0rem !important;
                    line-height: 0.9 !important;
                    padding-top:0.4rem !important;
                }

                h2{
                    font-family: 'Sora', sans-serif !important;
                    font-size: 1.9rem !important;
                    margin-bottom:0rem !important;
                    line-height: 0.9 !important;
                    padding-top:0.4rem !important;
                }

                h3,h4,p {
                    font-family: 'Inter', sans-serif !important;
                }

                button{
                    border-radius:1.5rem !important;
                    background:#2563EB !important;
                    color: white !important;
                    padding: 10px 20px !important;
                    border: none !important;
                    transition: transform 0.25s ease-in-out !important;
                }
                button:hover {
                    transform: scale(1.05) !important;
                }

                button[kind="secondary"]{
                    border-radius:1.5rem !important;
                    background:#5865F2 !important;
                    color: white !important;
                    padding: 10px 20px !important;
                    border:none !important;
                    transition: transform 0.25s ease-in-out !important;
                }
                button[kind-"Secondary"]:hover {
                    transform: scale(1.05) !important;
                }

                button[kind="tertiary"]{
                    border-radius:1.5rem !important;
                    background:#2563EB !important;
                    color: white !important;
                    padding: 10px 20px !important;
                    border:none !important;
                    transition: transform 0.25s ease-in-out !important;
                }
                button[kind-"tertiary"]:hover {
                    transform: scale(1.05) !important;
                }

        </style>
                
                """,unsafe_allow_html=True)