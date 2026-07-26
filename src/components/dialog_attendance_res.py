import streamlit as st
from src.database.config import supabase
from PIL import Image
import pandas as pd

@st.dialog("Face Attendance Report")
def save_photo_attendance(results,attendance_logs,session_data):
    st.write("Please review attendance before confirming")
    st.dataframe(results,hide_index=True,width="stretch")

    col1,col2 = st.columns(2)

    with col1:
        if st.button("Discard", width="stretch",key="image_discard",):
            if "session_data" in st.session_state:

                st.session_state.pop("session_data", None)
                st.session_state.pop("attendance_images", None)
                st.rerun()  # dialog will disappear so no attendance

    with col2:
            if st.button("Confirm & Save",key="image_confirm",width="stretch",type="primary"):
                try:
                    # 1. Create attendance session
                    st.write("Session data:", session_data)
                    existing = (
                    supabase.table("attendance_sessions")
                    .select("session_id")
                    .eq("subject_id", session_data["subject_id"])
                    .eq("attendance_date", session_data["attendance_date"])
                    .eq("lecture_number", session_data["lecture_number"])
                    .execute()
                )

                    
                    response = (
                        supabase.table("attendance_sessions")
                        .insert(session_data)
                        .execute()
                    )

                    if not response.data:
                        st.error("Failed to create attendance session.")
                        return

                    session_id = response.data[0]["session_id"]

                    # 2. Attach session_id to every attendance log
                    for log in attendance_logs:
                        log["session_id"] = session_id

                    # 3. Save attendance logs
                    logs_response = (
                        supabase.table("attendance_logs")
                        .insert(attendance_logs)
                        .execute()
                    )

                    if not logs_response.data:
                        st.error("Failed to save attendance logs.")
                        return

                    st.toast("Attendance saved successfully!")

                    st.session_state.pop("session_data", None)
                    st.session_state.pop("attendance_images", None)   # Face only
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to save attendance: {e}")


def save_voice_attendance(results,attendance_logs,session_data):
    st.write("Please review attendance before confirming")

    st.dataframe(results,hide_index=True,width="stretch")

    col1,col2 = st.columns(2)

    with col1:
        if st.button("Discard", width="stretch",key="voice_discard",):
            if "session_data" in st.session_state:

                st.session_state.pop("session_data", None)
                st.session_state.pop("voice_audio", None)
                st.session_state.pop("voice_results", None)
                st.session_state.pop("voice_logs", None)
                st.rerun()
             # dialog will disappear so no attendance

    with col2:
        if st.button("Confirm & Save",key="voice_confirm",width="stretch",type="primary"):
            try:
                existing = (
                    supabase.table("attendance_sessions")
                    .select("session_id")
                    .eq("subject_id", session_data["subject_id"])
                    .eq("attendance_date", session_data["attendance_date"])
                    .eq("lecture_number", session_data["lecture_number"])
                    .execute()
                )

                if existing.data:
                    st.error("Attendance already exists for this lecture.")
                    return
                
                # 1. Create attendance session

                response = (
                    supabase.table("attendance_sessions")
                    .insert(session_data)
                    .execute()
                )

                if not response.data:
                    st.error("Failed to create attendance session.")
                    return

                session_id = response.data[0]["session_id"]

                # 2. Attach session_id to every attendance log
                for log in attendance_logs:
                    log["session_id"] = session_id

                # 3. Save attendance logs
                logs_response = (
                    supabase.table("attendance_logs")
                    .insert(attendance_logs)
                    .execute()
                )

                if not logs_response.data:
                    st.error("Failed to save attendance logs.")
                    return

                st.toast("Attendance saved successfully!")
                st.session_state.pop("session_data", None)
                st.session_state.pop("voice_audio", None)  
                st.session_state.pop("voice_results", None)
                st.session_state.pop("voice_logs", None)
                st.rerun()


            except Exception as e:
                st.error(f"Failed to save attendance: {e}")
