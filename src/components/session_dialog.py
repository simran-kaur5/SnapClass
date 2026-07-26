import streamlit as st
from datetime import datetime

@st.dialog("Attendance Session")
def input_session(selected_subject_id):
    lecture_number = st.number_input("Lecture Number", min_value=1, step=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_time = st.time_input("Start Time")
    
    with col2:
        end_time = st.time_input("End Time")

    if st.button("Start", type="primary"):

        st.session_state.session_data = {
            "subject_id": selected_subject_id,
            "attendance_date": datetime.now().date().isoformat(),
            "lecture_number": lecture_number,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }

        st.rerun()

