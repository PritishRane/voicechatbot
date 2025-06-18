import os
import tempfile
import base64
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import speech_recognition as sr
from gtts import gTTS

# Always call this first in Streamlit
st.set_page_config(page_title="🎙️ Voice Chatbot", layout="centered")

# Load env vars
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Setup Groq LLM
llm = ChatGroq(api_key=groq_api_key, model_name="llama3-70b-8192")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="Hi! I'm your voice chatbot. Ask me anything!"),
    ]

# Title
st.title("🗣️ Voice Chatbot with Audio Reply")

# Record voice input
def transcribe_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        try:
            audio = r.listen(source, timeout=5)
            query = r.recognize_google(audio)
            return query
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand.")
        except sr.RequestError:
            st.error("Could not request results.")
        except sr.WaitTimeoutError:
            st.error("No speech detected.")
    return None

# Generate voice reply
def speak(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        with open(fp.name, "rb") as f:
            audio_bytes = f.read()
        b64_audio = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio autoplay controls>
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    os.remove(fp.name)

# Chat logic
def chat(query):
    st.session_state.messages.append(HumanMessage(content=query))
    reply = llm.invoke(st.session_state.messages)
    st.session_state.messages.append(reply)
    return reply.content

# Input section
st.subheader("🎤 Speak to Chatbot")

col1, col2 = st.columns([2, 1])
with col1:
    if st.button("🎙️ Click to Speak"):
        query = transcribe_voice()
        if query:
            st.success(f"You said: {query}")
            reply = chat(query)
            st.info(f"Bot: {reply}")
            speak(reply)

with col2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            AIMessage(content="Hi! I'm your voice chatbot. Ask me anything!")
        ]
        st.rerun()

# Display chat history
st.subheader("📜 Conversation History")
for msg in st.session_state.messages:
    role = "You" if isinstance(msg, HumanMessage) else "Bot"
    st.markdown(f"**{role}:** {msg.content}")
