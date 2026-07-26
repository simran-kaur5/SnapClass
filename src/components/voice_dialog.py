import streamlit as st
from src.database.config import supabase
from src.pipelines.voice_pipelines import process_bulk_audio
from src.components.dialog_attendance_res import save_voice_attendance

@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write("Record audio of students saying I am present. Then AI will recognize the students")

    audio_data = None

    audio_data = st.audio_input("Record classroom audio")


    if st.button("Analyze Audio",width="stretch",type="primary"):

        if audio_data is None:
            st.warning("Please record classroom audio first.")
            return

        
        with st.spinner("Processing Audio data"):
            enrolled_res = supabase.table("subject_students").select("*,students(*)").eq("subject_id",selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            # checking which which students have registered their voice
            if not enrolled_students:
                st.warning("No students enrolled in this course")
                return 

            # extract students ids of students which are enrolled
            student_ids = [
                row["student_id"]
                for row in enrolled_students
            ]

            # fetch all biometrices 
            biometrics_res = (
                supabase.table("student_biometrics")
                .select("student_id, voice_embedding")
                .in_("student_id", student_ids) # used _in because student_ids is list
                .execute()
            )

            candidates_dict = {
                row["student_id"] : row["voice_embedding"]
                for row in biometrics_res.data 
                if row["voice_embedding"] is not None # a student may not have registered voice
            }

            if not candidates_dict:
                st.error("No students have registered voice")
                return
            

            audio_bytes = audio_data.read()
            st.session_state.voice_audio = audio_bytes

            # first - voice embeddings , second - student_id,embeddings from database
            try:
                detected_scores = process_bulk_audio(st.session_state.voice_audio, candidates_dict)
            except Exception as e:
                st.error(f"Audio processing failed: {e}")
                return

            results,attendance_logs = [],[]
            
            
            for node in enrolled_students:
                student = node["students"]
                score = detected_scores.get(student["student_id"],0.0)
                is_present = bool(score>0)
            
                results.append({
                    "Name":student["name"],
                    "Roll No": student["roll_no"],
                    "Source": f"{score:.2f}" if is_present else "-",
                    "Status":"Present" if is_present else "Absent"
                })
            
                attendance_logs.append({
                    "student_id": student["student_id"],
                    "is_present": bool(is_present)
                })
            
            if "session_data" not in st.session_state:
                st.error("Please start an attendance session first.")
                return

            st.session_state.voice_results = results
            st.session_state.voice_logs = attendance_logs

    if "voice_results" in st.session_state:
        save_voice_attendance(
            st.session_state.voice_results,
            st.session_state.voice_logs,
            st.session_state.session_data,
        )