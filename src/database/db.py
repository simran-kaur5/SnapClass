from src.database.config import supabase

import bcrypt  # hash the password


def hash_pass(pss):
    return bcrypt.hashpw(pss.encode(),bcrypt.gensalt()).decode()


def check_pass(pss,hash_pss):
    return bcrypt.checkpw(pss.encode(),hash_pss.encode())

def check_teacher_username_exists(username):
    # check for unique username

    response = supabase.table("teachers").select("username").eq("username",username).execute()

    return len(response.data)>0

def check_teacher_email_exists(email):
    # check if email is already registered

    response = supabase.table("teachers").select("email").eq("email",email).execute()

    return len(response.data)>0

def create_teacher(username,password,name,email):
    data = {"username":username,
            "password_hash":hash_pass(password),
            "name":name,
            "email":email}
    response = supabase.table("teachers").insert(data).execute()

    return response.data


def login_teacher(username_email,password):
    # either user can login with email or username
    response = (
    supabase.table("teachers")
    .select("*")
    .or_(f"username.eq.{username_email},email.eq.{username_email}")
    .execute()
)

    if response.data:
        teacher = response.data[0]

        if check_pass(password,teacher["password_hash"]):
            return teacher
    return None


def get_students():
    response = (
        supabase.table("student_biometrics")
        .select("""
            student_id,
            face_embedding,
            students(
                student_id,
                name,
                roll_no,
                email
            )
        """)
        .execute()
    )

    return response.data

def create_acc(roll_no, name, email, face_embedding, voice_embedding):
    student = (
        supabase.table("students")
        .insert({
            "roll_no": roll_no,
            "name": name,
            "email": email
        })
        .execute()
    )

    student_id = student.data[0]["student_id"]

    supabase.table("student_biometrics").insert({
        "student_id": student_id,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }).execute()

    return student.data

def create_subject(sub_name,sub_id,sub_section,teacher_id):
    subject = (
        supabase.table("subjects")
        .insert({
            "subject_code":sub_id,
            "name":sub_name,
            "section":sub_section,
            "teacher_id":teacher_id
        })
        .execute()
    )

    return subject.data

def get_teacher_subjects(teacher_id):
    response = (
        supabase.table("subjects")
        .select("""
            subject_id,
            subject_code,
            name,
            section,
            subject_students(student_id),
            attendance_sessions(session_id)
        """)
        .eq("teacher_id", teacher_id)
        .order("subject_code")
        .order("section")
        .execute()
    )

    return response.data

def update_subject(subject_id, code, name, section):
    response = (
        supabase.table("subjects")
        .update({
            "subject_code": code,
            "name": name,
            "section": section
        })
        .eq("subject_id", subject_id)
        .execute()
    )

    return response.data


def delete_subject(subject_id):
    response = (
        supabase.table("subjects")
        .delete()
        .eq("subject_id", subject_id)
        .execute()
    )

    return response.data

def get_subject_students(subject_id):

    response = (
        supabase.table("subject_students")
        .select("""
            students(
                roll_no,
                name
            )
        """)
        .eq("subject_id", subject_id)
        .execute()
    )

    return response.data

def enroll_student_subject(subject_id,student_id):
    data = {"student_id":student_id,"subject_id":subject_id}

    response= supabase.table("subject_students").insert(data).execute()

    return response.data

def unenroll_student_subject(subject_id, student_id):
    response = (
        supabase.table("subject_students")
        .delete()
        .eq("student_id", student_id)
        .eq("subject_id", subject_id)
        .execute()
    )

    return response.data

def get_student_subjects(student_id):
    response =supabase.table("subject_students").select("*,subjects(*)").eq("student_id",student_id).execute()
    return response.data

def get_student_attendance(student_id):
    # runned one PostgreSQL Query to join three tables in Supabase and then called it here
    response = (
        supabase.rpc(
            "get_student_attendance_summary",
            {"p_student_id": student_id}
        ).execute()
    )

    return response.data


# def save_attendace():
#     response = supabase.table("attendance_logs").insert(attendance_logs).execute()
#     return response.data

def get_teacher_record(teacher_id):
    response = (
        supabase.table("attendance_logs")
        .select("""
            *,
            attendance_sessions!inner(
                attendance_date,
                lecture_number,
                start_time,
                end_time,
                subjects!inner(
                    name,
                    subject_code,
                    teacher_id
                )
            )
        """)
        .eq("attendance_sessions.subjects.teacher_id", teacher_id)
        .execute()
    )

    return response.data