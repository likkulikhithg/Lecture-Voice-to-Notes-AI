import streamlit as st
import whisper
from transformers import pipeline
import tempfile

st.set_page_config(page_title="Lecture Voice-to-Notes AI")

st.title("🎙 Lecture Voice-to-Notes AI")
st.write("Upload lecture audio and generate transcript, summary, quiz, and flashcards.")

@st.cache_resource
def load_models():
    whisper_model = whisper.load_model("tiny")
    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6"
    )
    return whisper_model, summarizer

whisper_model, summarizer = load_models()

uploaded_file = st.file_uploader("Upload Audio or Video", type=["mp3", "wav", "mp4"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    st.info("Transcribing...")

    result = whisper_model.transcribe(temp_path)
    transcript = result["text"]

    st.subheader(" Transcript")
    st.write(transcript)

    st.info("Generating summary...")

    summary = summarizer(transcript, max_length=200, min_length=50, do_sample=False)
    notes = summary[0]["summary_text"]

    st.subheader(" Smart Summary")
    st.write(notes)

    sentences = transcript.split(".")

    st.subheader(" Quiz Questions")
    for i, s in enumerate(sentences[:5]):
        st.write(f"Q{i+1}: Explain: {s.strip()}?")

    st.subheader(" Flashcards")
    for i, s in enumerate(sentences[:5]):
        st.write(f"Flashcard {i+1}")
        st.write(f"Front: {s.strip()}")
        st.write("Back: Explanation")
        st.write("---")