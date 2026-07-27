import streamlit as st
from src.components.header import header_dashboard
from src.ui.base_layout import style_base_layout
from src.components.footer import footer_dashboard
import numpy as np
from PIL import Image  # image processing library
from src.pipelines.face_pipelines import predict_attendance, get_face_embeddings,train_classifier
from src.pipelines.voice_pipelines import get_voice_embeddings
from src.database.db import get_students,create_acc,get_student_attendance,get_student_subjects,unenroll_student_subject
import time
from src.components.dialog_enroll_student import enroll_dialog
from src.components.subject_card import subject_card
    
def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data["student_id"]

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']}")
        if(st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace")):
            st.session_state["is_logged_in"]=False
            del st.session_state["student_data"]
            st.rerun()

    col1,col2 = st.columns(2)

    with col1:
        st.write("Your enrolled Subjects")
    with col2:
        if st.button("Enroll in Subject",type="primary",width="stretch"):
            enroll_dialog()

    st.divider()


# display student subjects and attendance logs
    with st.spinner("Loading your enrolled Subjects.."):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)
    
    state_map = {} # will store attendance stats

    state_map = {}

    for log in logs:
        sid = log["subject_id"]

        state_map[sid] = {
            "total": log["total_classes"],
            "attendance": log["attended_classes"]
        }


    
    cols= st.columns(2)

    for i,sub_code in enumerate(subjects):
        sub = sub_code["subjects"] # dicitonary of subjects
        sid = sub["subject_id"]

        stats = state_map.get(sid,{"total":0,"attendance":0})

        def unroll_button(subject_id):
            if st.button(
                "Unenroll from this course",
                type="tertiary",
                key=f"unenroll_{subject_id}",
                width="stretch",
                icon=":material/delete_forever:"
            ):
                unenroll_student_subject(subject_id, student_id)
                st.toast("Unenrolled from the course")
                st.rerun()
        with cols[i%2]:

            subject_card(
                name=sub["name"],
                code=sub["subject_code"],
                section=sub["section"],
                state=[
                    {"Total": stats["total"]},
                    {"Attended": stats["attendance"]},
                    {"Absent": stats["total"] - stats["attendance"]},
                    {
                        "Attendance": f"{(stats['attendance'] / stats['total'] * 100):.1f}%"
                        if stats["total"] > 0 else "0%"
                    },
                ],
                footer_callback=lambda: unroll_button(sid)
            )
        

    footer_dashboard()

def student_screen():

    if "student_data" in st.session_state:
        student_dashboard()
        return 

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()
    with c2:
        if(st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace")):
            st.session_state["login_type"]=None
            st.rerun()

    st.markdown("""
        <div style="display:flex; justify-content:center;">
            <h2>Login using FaceID</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.space()
    st.space()

    
    photo_source = st.camera_input("Position your face in the center")
    show_regis = False

    if photo_source:
        image = Image.open(photo_source)
        image_np = np.array(image)

        with st.spinner("AI is scanning"):
            detected,all_ids ,num_faces= predict_attendance(image_np)

            if num_faces == 0:
                st.warning("Face not found")
            elif num_faces>1:
                st.warning("Multiple faces found")
            else:
                if detected:
                    student_id = list(detected.keys())[0] #.keys gives id=> dict_keys([8])
                    all_students = get_students()
                    student = next((s for s in all_students if s["student_id"]==student_id),None)

                    if student:
                       student_info = student["students"] # take only student part from table
                       st.session_state.is_logged_in = True
                       st.session_state.user_role = "student"
                       st.session_state.student_data = student_info
                       st.toast(f"Welcome Back {student_info["name"]}")
                       time.sleep(1)
                       st.rerun()      
                        
                else:
                    st.info("Face not recognized! You might be a new student")
                    show_regis = True
                    
    if show_regis: # if face not recog means the student is new
        with st.container(border=True):
           st.header("Register new profile")
           roll_no = st.text_input("Roll Number")
           new_name = st.text_input("Name")
           email = st.text_input("Email")

           st.subheader("Optional : Voice Enrollement")
           st.info("Voice enroll for attendance")

           audio_data = None

           try:
               audio_data = st.audio_input("Record a short phrase like I am present , my name is Bob")
           except Exception:
               st.error("Audio data failed")

            
           if st.button("Create new account",type = 'primary'):
               if new_name and roll_no and email:
                   with st.spinner("Creating Profile..."):
                       image = np.array(Image.open(photo_source))
                       face_encoding = get_face_embeddings(image)

                       if face_encoding:
                           face_emb = face_encoding[0].tolist()

                           voice_emb = None
                           if audio_data:
                               voice_emb = get_voice_embeddings(audio_data.read())

                           response_data  = create_acc(
                                    roll_no=roll_no,
                                    name=new_name,
                                    email=email,
                                    face_embedding=face_emb,
                                    voice_embedding=voice_emb
                                )

                            
                           if response_data:
                               train_classifier()
                               st.session_state.is_logged_in = True
                               st.session_state.user_role = "student"
                               st.session_state.student_data = response_data[0]
                               st.toast(f"Profile created! Hi {new_name}")  
                               time.sleep(1)
                               st.rerun()      
                       else:
                           st.error("Couldn't capture you facial features for registrations")

               else:
                   st.warning("Please fill all the fields")

                
    footer_dashboard()