import streamlit as st
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_teacher_username_exists,create_teacher,login_teacher,check_teacher_email_exists,get_teacher_subjects,update_subject,delete_subject,get_teacher_record
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_button import share_dailog_button
from src.components.photos_dailog import add_photos_dialog
import numpy as np
from src.database.config import supabase
from src.pipelines.face_pipelines import predict_attendance
from src.components.dialog_attendance_res import save_photo_attendance
from src.components.session_dialog import input_session
from src.components.voice_dialog import voice_attendance_dialog
import pandas as pd
from datetime import datetime

def teacher_dashboard():
    if "teacher_data" in st.session_state:
        #login to teacher portal
        teacher_screen()
        return 

    if "teacher_login_type" not in st.session_state:
        st.session_state.teacher_login_type = "login"

    if st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    else:
        teacher_screen_register()


def teacher_screen():
    teacher_data = st.session_state.teacher_data

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {teacher_data['name']}")
        if(st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace")):
            st.session_state["is_logged_in"]=False
            del st.session_state["teacher_data"]
            st.rerun()

    

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "attendance_take"

    tab1 ,tab2,tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == "attendance_take" else "tertiary"
        if st.button("Take Attendance",type=type1,width="stretch",icon=":material/ar_on_you:"):
            st.session_state.current_teacher_tab = "attendance_take"
            st.rerun()
    
    with tab2:
        type1 = "primary" if st.session_state.current_teacher_tab == "manage_sub" else "tertiary"
        if st.button("Manage Subjects",type=type1,width="stretch",icon=":material/book_ribbon:"):
            st.session_state.current_teacher_tab = "manage_sub"
            st.rerun()
    
    with tab3:
        type1 = "primary" if st.session_state.current_teacher_tab == "attendance_records" else "tertiary"
        if st.button("Attendance Records",type=type1,width="stretch",icon=":material/cards_stack:"):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()


    st.divider()


    if st.session_state.current_teacher_tab == "attendance_take":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_sub":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_rec()
    

    footer_dashboard()


# allow teacher to edit the Subject details
@st.dialog("Edit Subject")
def edit_subject_dialog(subject):

    code = st.text_input(
        "Subject Code",
        value=subject["subject_code"]
    )

    name = st.text_input(
        "Subject Name",
        value=subject["name"]
    )

    section = st.text_input(
        "Section",
        value=subject["section"]
    )

    if st.button("Save Changes", type="primary"):

        if not code or not name or not section:
            st.error("All fields are required.")
            return

        try:
            update_subject(
                subject["subject_id"],
                code,
                name,
                section
            )

            st.success("Subject updated successfully!")
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

# delete the Subject
@st.dialog("Delete Subject")
def delete_subject_dialog(subject):

    st.warning(
        f"Are you sure you want to delete **{subject['name']} "
        f"(Section {subject['section']})**?"
    )

    st.write("This action cannot be undone.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

    with col2:
        if st.button(
            "Delete",
            type="primary",
            use_container_width=True
        ):
            try:
                delete_subject(subject["subject_id"])

                st.toast("Subject deleted successfully.")
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")


def teacher_tab_take_attendance():

    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take Attendance")

    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning("You haven't created any subjects yet! Please create one to begin!")
        return

    subject_options = {f"{s['name']} - {s['section']}":s['subject_id'] for s in subjects}  # dictionary comprehension
    # key = "DBMS - 1" => value = 1

    col1, col2 = st.columns([3,1],vertical_alignment="bottom")

    with col1:

        selected_subject_label = st.selectbox(
            "Select Subject",
            options=list(subject_options.keys()),
            disabled="session_data" in st.session_state #disable selectbox after procedding next
        )

    with col2:
        if st.button("Start Attendance", type="primary",disabled="session_data" in st.session_state):
            input_session(subject_options[selected_subject_label])

    selected_subject_id = subject_options[selected_subject_label]

    if "session_data" in st.session_state:

    # show add photos button
        if st.button(
            "Add Photos",
            type="primary",
            icon=":material/photo_prints:"
        ):
            add_photos_dialog()



        if st.session_state.attendance_images:
            st.header("Added Photos")
            gallery_cols = st.columns(4)

            for idx,img in enumerate(st.session_state.attendance_images):
                with gallery_cols[idx % 4]:
                    st.image(img,width="stretch",caption=f"Photo {idx+1}")


        c1, c2, c3 = st.columns(3)
        has_photos = bool(st.session_state.attendance_images)
        with c1:
            if st.button("Clear all photos",width="stretch",type="tertiary",disabled= not has_photos,icon=":material/delete:"):
                st.session_state.attendance_images = []

        with c2:

            if st.button("Run Face Analysis",disabled=not has_photos,width="stretch",type="secondary",icon=":material/analytics:"):
                with st.spinner("Deep scanning classroom photos..."):
                    all_detected_ids = {}

                    for idx,img in enumerate(st.session_state.attendance_images):
                        image_np = np.array(img.convert("RGB")) # beacuse we saved image in open form
                        detected,_,_ = predict_attendance(image_np)

                        if detected:
                            for sid in detected:
                                student_id = int(sid)

                                all_detected_ids.setdefault(student_id,[]).append(f"Photo {idx+1}") # push the id of the students who capured
                                # like {8: ["Photo 1", "Photo 3", "Photo 5"]} 

                    enrolled_res = supabase.table("subject_students").select("*,students(*)").eq("subject_id",st.session_state.session_data["subject_id"]).execute()

                    enrolled_students = enrolled_res.data  # all students in that course

                    if not enrolled_students:
                        st.warning("No students enrolled in this course")
                    else:

                        results,attendance_logs = [],[]


                        for node in enrolled_students:
                            student = node["students"]
                            sources = all_detected_ids.get(int(student["student_id"]),[])
                            is_present = len(sources)>0  # if student is present in multiple photos => mark it present only once

                            results.append({
                                "Name":student["name"],
                                "Roll No": student["roll_no"],
                                "Source":",".join(sources) if is_present else "-",
                                "Status":"Present" if is_present else "Absent"
                            })

                            attendance_logs.append({
                                "student_id": student["student_id"],
                                "is_present": bool(is_present)
                            })

                        save_photo_attendance(results,attendance_logs,st.session_state.session_data)

        with c3:
            if st.button("Use Voice Attendance",type="primary",width="stretch",icon=":material/mic:"):
                voice_attendance_dialog(selected_subject_id)


    st.divider()

def teacher_tab_manage_subjects():

    teacher_id = st.session_state.teacher_data["teacher_id"]

    col1, col2 = st.columns([4,2])

    with col1:
        st.header("Manage Subjects")

    with col2:
        if st.button("Create new Subject", use_container_width=True):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.info("No subjects found.")
        return
    
    st.markdown("""
        <style>

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: white !important;
            border-radius: 16px !important;
            padding: 20px !important;
            border: 1px solid #e5e7eb !important;
        }

        </style>
        """, unsafe_allow_html=True)

    for subject in subjects:

        total_students = len(subject["subject_students"])
        total_classes = len(subject["attendance_sessions"])

        with st.container(border=True):

            st.subheader(f"{subject['name']}")

            c1, c2 = st.columns(2)

            with c1:
                st.write(f"**Code:** {subject['subject_code']}")

            with c2:
                st.write(f"**Section:** {subject['section']}")


            c3, c4 = st.columns(2)

            with c3:
                st.write(f"👨‍🎓 Students: {total_students}")

            with c4:
                st.write(f"Classes Taken: {total_classes}")


            b1, b2 = st.columns(2)

            with b1:
                if st.button(
                    "Edit",
                    key=f"edit_{subject['subject_id']}",
                    type="primary"
                ):
                    edit_subject_dialog(subject)

            with b2:
                if st.button(
                    "Delete",
                    key=f"delete_{subject['subject_id']}",
                    type="primary"
                ):
                    delete_subject_dialog(subject) 


            if st.button(
                f"Share QR Code",
                key=f"share_{subject['subject_id']}",
                icon=":material/share:",
                type="primary"
            ):
                share_dailog_button(
                    subject["name"],
                    subject["subject_code"]
                )

                     
                

def teacher_tab_attendance_rec():
    st.header("Records")

    teacher_id = st.session_state.teacher_data["teacher_id"]

    records = get_teacher_record(teacher_id)

    if not records:
        st.error("You have not any records")
        return

    data = []

    for r in records:
        # Get attendance session details (date, lecture, subject, etc.)
        session = r["attendance_sessions"]

         # Extract only the fields needed for the records table
        time = datetime.strptime(
            session["start_time"], "%H:%M:%S"
        ).strftime("%I:%M %p")

        data.append({
            "Date": session["attendance_date"],
            "Time": time,
            "Lecture": session["lecture_number"],
            "Subject": session["subjects"]["name"],
            "Subject Code": session["subjects"]["subject_code"],
            "Present": r["is_present"]
        })

    df = pd.DataFrame(data)

    # Group records by lecture and calculate attendance summary
    summary = (df.groupby(["Date","Time","Lecture","Subject","Subject Code"])
    .agg(
        Present_Count = ("Present","sum"),
        Total_count = ("Present","count")
    ).reset_index())

    # Create attendance summary in the format "Present/Total Students"
    summary["Attendance Stats"] = (
        summary["Present_Count"].astype(str) + "/"
        + summary["Total_count"].astype(str) + "Students"
    )

    display_df = (summary.sort_values(["Date", "Lecture"],ascending=True)
                    [["Date","Time","Lecture","Subject","Subject Code","Attendance Stats"]])

    st.dataframe(display_df,width="stretch",hide_index=True)



def teacher_reg(teacher_username, teacher_password, teacher_name, teacher_email, confirm_pass):
    # if user left any field empty
    if not teacher_username or not teacher_email or not teacher_name or not teacher_password:
        return False ,"All Fields are required"
    if check_teacher_email_exists(teacher_email):
        return False ,"Email is already registered"
    if check_teacher_username_exists(teacher_username):
        return False,"Username is already taken" 
    if teacher_password != confirm_pass:
        return False , "Password doesn't match"
    
    try:
        create_teacher(teacher_username,teacher_password,teacher_name,teacher_email)
        return True,"Successfully registered! Login Now"
    except Exception as e:
        return False,str(e)
    
def teacher_login(username_email, password):
    if not username_email:
        return False, "Enter username or Email"

    if not password:
        return False, "Enter the password"

    teacher = login_teacher(username_email, password)

    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.logged_in = True
        return True, "Welcome Back"

    return False, "Invalid username/email or password"
    

def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()
    with c2:
        if(st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace")):
            st.session_state["login_type"]=None
            st.rerun()

    st.markdown("""
        <div style="display:flex; justify-content:center;">
            <h2>Login using password</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.space() # add space
    st.space()

    teacher_username_email = st.text_input("Enter username or Email",placeholder="@bob123")
    teacher_password = st.text_input("Enter password",type="password",placeholder="password")

    
    st.divider() # add very thin line after

    # add buttons

    btn1,btn2 = st.columns(2)

    with btn1:
        if(st.button("Login",icon=":material/passkey:",shortcut="command+Enter",key="Login",width="stretch")): # google icon library used by 
            success,message = teacher_login(teacher_username_email,teacher_password)
            if(success):
                st.toast("Welcome Back")
                import time
                time.sleep(1)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)
    with btn2:
        if(st.button("Register",type="primary",icon=":material/passkey:",key="Register",width="stretch")):
            st.session_state.teacher_login_type = "register"
            st.rerun()

    footer_dashboard()


def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()
    with c2:
        if(st.button("Go back to Home", type='secondary', key='backbtn', shortcut="control+backspace")):
            st.session_state["login_type"]=None
            st.rerun()

    st.markdown("""
        <div style="display:flex; justify-content:center;">
            <h2>Register to teacher portal</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.space()
    st.space()

    teacher_username = st.text_input("Enter username",placeholder="@bob123")
    teacher_email = st.text_input("Enter your email",placeholder="bob@gmail.com")
    teacher_name = st.text_input("Enter name",placeholder="Bob")
    teacher_password = st.text_input("Enter your password",type="password",placeholder="password")
    confirm_pass = st.text_input("Confirm password",type="password",placeholder="Confirm your password")

    
    st.divider()

    btn1,btn2 = st.columns(2)

    with btn1:
        if(st.button("Register",type="primary",icon=":material/passkey:",key="Register",width="stretch")):
            success , message = teacher_reg(teacher_username, teacher_password, teacher_name, teacher_email, confirm_pass)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)
    with btn2:
        if(st.button("Login",icon=":material/passkey:",shortcut="command+Enter",key="Login",width="stretch")):
            st.session_state.teacher_login_type="login"
            st.rerun()
        
    footer_dashboard()