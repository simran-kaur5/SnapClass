import streamlit as st
from src.database.db import create_subject


@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new subject")
    sub_id = st.text_input("Enter Subject ID",placeholder="CS101")
    sub_name = st.text_input("Enter Subject Name",placeholder="Computer Science")
    sub_section = st.text_input("Enter section",placeholder="A")

    if st.button("Create Subject now",type= "primary",width="stretch"):
        if sub_name and sub_id and sub_section:
            try:
                create_subject(sub_name,sub_id,sub_section,teacher_id)
                st.toast("Subject created Successfully!!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning(f"Please fill all the fields")



