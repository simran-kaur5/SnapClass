import streamlit as st
import dlib
import face_recognition_models  #pretrained models
from sklearn.svm import SVC
import numpy as np

from src.database.db import get_students

@st.cache_resource # by this we dont load models again and again once loaded save into memory
def load_dlib_models():

    # detects that face exists -> face rectangle(left,right,top,bottom)
    detector = dlib.get_frontal_face_detector() 

    # detector gives face
    # this predicts -> left eye,right eyes, lips,jawline => 68 landmarks points
    shape_pred = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    # its deep learning model
    # it returns face embeddings => embeddings of every person is unique
    # 128 values
    face_recog = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector , shape_pred , face_recog

def get_face_embeddings(np_image):

    detector , shape_pred , face_recog = load_dlib_models()

    faces = detector(np_image,1) # ex -> detector searches 10 faces in image

    encoding = []

    for face in faces:

        shape = shape_pred(np_image,face) # 68 facial landmarks

        # NN converts big image size to 128 dim vector => embeddings
        face_descriptor = face_recog.compute_face_descriptor(np_image,shape,1)

        encoding.append(np.array(face_descriptor))

    return encoding

@st.cache_resource
# this fun =>Read all students from the database and train an SVM classifier.
def get_trained_model():

    X = [] # store embeddings=> input
    y = [] # ids => output

    students_db = get_students()

    if not students_db: # if no any student in database return None
        return None
    
    for student in students_db:

        embeddings = student.get("face_embedding")
        ids = student.get("student_id")

        if embeddings: # if student not recognized then its empty
            X.append(np.array(embeddings))
            y.append(ids)

        
    if len(X)==0:
        return 0
    
    svc = SVC(kernel="linear",probability=True,class_weight="balanced") # also returns confidence score

    try:
        svc.fit(X,y)
    except ValueError:
        pass

    # return trained_svm,embedding,ids
    return {"svc":svc,"X":X,"y":y}

# when new student comes
def train_classifier():
    # remove the old memory of model
    st.cache_resource.clear()

    # retrain the model
    model_data = get_trained_model()

    return bool(model_data) # returns true if training was successful

def predict_attendance(class_image_np):

    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    model_data = get_trained_model() # get trained model

    if not model_data:
        # not recog, empty_list for unknown faces ,total face
        return detected_student,[],len(encodings) # prediction cannot happen
    
    svc = model_data['svc']
    X_train = model_data["X"]
    y_train = model_data["y"]

    all_students = sorted(list(set(y_train))) # remove duplicates

    for encoding in encodings:
        # SVM requires at leat two classes 
        if len(all_students)>=2:
            predicted_id = int(svc.predict([encoding])[0])  # its returns an array but take only id
        else:
            predicted_id = int(all_students[0]) # one student present in database so no need to predict

        student_embedding = X_train[y_train.index(predicted_id)] # search the index of that predicted_id and saves embeddings of that index

        best_match_score = np.linalg.norm(student_embedding-encoding)

        resemblance_threshold = 0.45 # differnce between the predicted phto and org img but nor exceed this

        if best_match_score<=resemblance_threshold:
            detected_student[predicted_id] = True

        print(f"Predicted ID: {predicted_id}")
        print(f"Distance: {best_match_score}")
        print(f"Threshold: {resemblance_threshold}")
        print(detected_student)

    return  detected_student,all_students,len(encodings)