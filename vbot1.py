import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import uuid
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-70b-8192",
    temperature=0.7,
    max_tokens=1024,
)

# Session state to track audio
if 'audio_playing' not in st.session_state:
    st.session_state.audio_playing = False
if 'temp_audio' not in st.session_state:
    st.session_state.temp_audio = ""

# Function: Speak text using gTTS + pygame (non-blocking)
def speak(text):
    temp_path = f"temp_{uuid.uuid4()}.mp3"
    tts = gTTS(text)
    tts.save(temp_path)

    pygame.mixer.init()
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()

    st.session_state.temp_audio = temp_path
    st.session_state.audio_playing = True

# Function: Stop audio
def stop_audio():
    if st.session_state.audio_playing:
        pygame.mixer.music.stop()
        st.session_state.audio_playing = False
        if os.path.exists(st.session_state.temp_audio):
            os.remove(st.session_state.temp_audio)
        st.session_state.temp_audio = ""

# Function: Transcribe voice to text
def transcribe_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand you."
    except sr.RequestError:
        return "Speech recognition service error."

# Function: Get LLM reply
def chat_with_groq(prompt):
    messages = [
        SystemMessage(content="You are a helpful voice assistant."),
        HumanMessage(content=prompt)
    ]
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.set_page_config(page_title="🎙️ Voice Chatbot", layout="centered")
st.title("🎙️ Voice Chatbot with Groq LLaMA3")

# Stop audio button
if st.session_state.audio_playing:
    if st.button("🔇 Stop Audio"):
        stop_audio()
        st.info("Audio stopped.")

# Speak button
if st.button("🎤 Speak Now"):
    stop_audio()  # Stop any currently playing audio
    user_input = transcribe_voice()
    st.write(f"**You said:** {user_input}")

    if user_input:
        with st.spinner("Thinking..."):
            reply = chat_with_groq(user_input)
            st.success(reply)
            speak(reply)