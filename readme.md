# SnapClass – AI Powered Attendance Management System

SnapClass is an AI-powered attendance management system that automates classroom attendance using **Face Recognition** and **Voice Recognition**. The application provides separate dashboards for teachers and students, making attendance faster, secure, and easier to manage.

---

## Features

### Teacher

- Secure Login
- Create and Manage Subjects
- Generate QR Codes for Student Enrollment
- Face Recognition Attendance
- Voice Recognition Attendance
- Attendance Records
- Attendance Statistics

### Student

- Student Registration
- Join Subjects using QR Code
- Face Registration
- Voice Registration
- Personal Dashboard
- Attendance History

---

## Technologies Used

### Frontend

- Streamlit

### Backend

- Python

### Database

- Supabase (PostgreSQL)

### Machine Learning

- Face Recognition
- Dlib
- Scikit-learn
- Resemblyzer
- Librosa

### Other Libraries

- NumPy
- Pandas
- Pillow
- Bcrypt
- Segno

---

## Installation

Clone the repository

```bash
git clone https://github.com/simran-kaur5/SnapClass.git
```

Move into the project directory

```bash
cd SnapClass
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.streamlit/secrets.toml` file.

Add your Supabase credentials:

```toml
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
```

---

## Run the Project

```bash
streamlit run app.py
```

---

## Demo

Live Application

https://smart-snapclass.streamlit.app/

Landing Page

(Add your landing page URL after deployment)

---

## Application Workflow

### Teacher

1. Register/Login
2. Create Subjects
3. Share QR Code
4. Students Join Subject
5. Take Attendance
   - Face Recognition
   - Voice Recognition
6. View Attendance Reports

### Student

1. Register
2. Join Subject
3. Register Face
4. Register Voice
5. View Attendance

---

## Future Improvements

- Liveness Detection
- Attendance Analytics Dashboard
- Email Notifications
- Multi-Face Recognition Optimization
- Mobile Application
- OCR-based Student Verification

---

## Screenshots

You can add screenshots of:

- Home Screen
- Teacher Dashboard
- Student Dashboard
- Face Attendance
- Voice Attendance
- QR Enrollment
- Attendance Records

---

## Author

**Simranjit Kaur**

B.Tech Computer Science Engineering

GitHub: https://github.com/simran-kaur5

---

## License

This project is developed for educational and portfolio purposes.