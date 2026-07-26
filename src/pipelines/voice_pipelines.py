from resemblyzer import VoiceEncoder,preprocess_wav
import numpy as np
import io
import librosa
import streamlit as st

@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()

# when student register store embeddings in DB
def get_voice_embeddings(audio_bytes):

    try:
        encoder = load_voice_encoder()

        audio,sr = librosa.load(io.BytesIO(audio_bytes),sr=16000)

        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)

        return embedding.tolist() #JS processes good in list instead of Array
    
    except Exception as e:
        st.error("Voice recog error")

# while attendance student speaks => match its embeddings stored in DB
def indentify_speaker(new_embeddings,candidate_dict,threshold=0.65):
    if new_embeddings is None or not candidate_dict:
        return None,0.0 # best_id and best_score
    
    best_sid = None  #take best_id by which the audio is matching
    best_score =-1.0

    for sid,stored_embeddings in candidate_dict.items():
        if stored_embeddings:
            similarity = np.dot(new_embeddings,stored_embeddings) # higher value => higher similarity

            if similarity>best_score:
                best_score = similarity
                best_sid = sid

    if best_score>=threshold:
        return best_sid,best_score

    return None,best_score

def process_bulk_audio(audio_bytes,candidates_dict,threshold=0.65):

    try:
        encoder = load_voice_encoder()

        audio,sr = librosa.load(io.BytesIO(audio_bytes),sr=16000)

        # detects speech and silence
        segments = librosa.effects.split(audio,top_db=30)

        identified_result = {}

        for start , end in segments:

            if(end-start)<sr*0.5:
                continue

            segment_audio = audio[start:end]

            wav = preprocess_wav(segment_audio)

            embedding = encoder.embed_utterance(wav)

            sid,score = indentify_speaker(embedding,candidates_dict,threshold)


            if sid: 
                if sid not in identified_result or score > identified_result[sid]:
                    identified_result[sid] = score

        
        return identified_result
    
    except Exception as e:
        st.error("Bulk process error")
        return {}


    

