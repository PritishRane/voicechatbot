import os
import tempfile
import base64
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from gtts import gTTS

st.set_page_config(page_title="🎙️ Chatbot", layout="centered")

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(api_key=groq_api_key, model_name="llama3-70b-8192")

if "messages" not in st.session_state:
    st.session_state.messages = [AIMessage(content="Hello! Ask me anything.")]

st.title("🗨️ Chatbot with Voice Reply")

# Text-to-speech
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

# Input UI
query = st.text_input("Type your question here:")

if st.button("Send") and query:
    reply = chat(query)
    st.success(f"Bot: {reply}")
    speak(reply)

if st.button("Clear Chat"):
    st.session_state.messages = [AIMessage(content="Hello! Ask me anything.")]
    st.rerun()

# Show chat history
st.subheader("📜 Chat History")
for msg in st.session_state.messages:
    role = "You" if isinstance(msg, HumanMessage) else "Bot"
    st.markdown(f"**{role}:** {msg.content}")
