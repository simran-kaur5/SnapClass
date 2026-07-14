import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home

def home():
    header_home()

    col1,col2 = st.columns(2,gap="large")

    with col1:
        st.markdown(
            """
            <h2 style="margin-top: 50px;">
                I am a Student
            </h2>
            """,
            unsafe_allow_html=True
        )
        st.image("https://i.ibb.co/844D9Lrt/mascot-student.png", width=123)

        if st.button("Student Portal",type="primary", key="student-home-btn",icon=":material/arrow_outward:",icon_position="right"):
            st.session_state["login_type"] = "student"
            st.rerun()

    with col2:
        st.markdown(
            """
            <h2 style="margin-top: 50px;">
                I am a Teacher
            </h2>
            """,
            unsafe_allow_html=True
        )
        st.image("https://i.ibb.co/CsmQQV6X/mascot-teacher.png", width=150)

        if st.button("Teacher Portal", key="teacher-home-btn",type="primary",icon=":material/arrow_outward:",icon_position="right"):
            st.session_state["login_type"] = "teacher"
            st.rerun()
        
    footer_home()