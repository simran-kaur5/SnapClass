import streamlit as st
from src.screens.home_screen import home
from src.screens.student_screen import student
from src.screens.teacher_screen import teacher
from src.components.header import header_home
from src.ui.base_layout import home_background,base_style

base_style()
home_background()


def main():

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None
    
    if st.session_state['login_type'] == "teacher":
        teacher()

        
    elif st.session_state['login_type'] == "student":
        student()
    else:
        home()

main()