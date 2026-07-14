import streamlit as st

def header_home():
    
    st.markdown("""
        <div style="text-align:center; margin-top:30px">
            <img src="https://i.ibb.co/YTYGn5qV/logo.png" style="height:120px;">
            <h1>Snap<br> <span style="display:inline-block; margin-left:20px;">
                Class
            </span></h1>
        </div>
                """
                , unsafe_allow_html=True)

# def header_student():
#     st.button("Student-HOME",key="stu-header")

# def header_teacher():
#     st.button("Teacher-HOME",key="tea-header")