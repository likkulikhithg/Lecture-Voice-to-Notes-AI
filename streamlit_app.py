import streamlit as st
from openai import OpenAI
import tempfile

# Page config
st.set_page_config(
    page_title="Lecture Voice-to-Notes AI",
    page_icon="🎙",
    layout="wide"
)

st.title("🎙 Lecture Voice-to-Notes AI")
st.markdown("Upload a lecture audio file and automatically generate transcript, summary, quiz questions, and flashcards.")

# Load OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["lecturetotranscript"])

uploaded_file = st.file_uploader(
    "Upload Audio File",
    type=["mp3", "wav", "m4a"],
)

if uploaded_file:

    with st.spinner("Transcribing audio..."):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        # Transcribe using OpenAI
        with open(temp_path, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file
            )

        transcript = transcript_response.text

    st.subheader("Transcript")
    st.write(transcript)

    with st.spinner("Generating study materials..."):

        prompt = f"""
        From the following lecture transcript:

        {transcript}

        Generate:
        1. A clean, structured study summary.
        2. 5 quiz questions with answers.
        3. 5 flashcards in Q/A format.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        output = response.choices[0].message.content

    st.subheader(" AI Generated Study Materials")
    st.write(output)

st.markdown("---")