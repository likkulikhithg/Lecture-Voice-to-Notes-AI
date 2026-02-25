import streamlit as st
import requests
import time
from groq import Groq
import tempfile

st.set_page_config(page_title="Lecture Voice-to-Notes AI")

st.title("🎙 Lecture Voice-to-Notes AI (Fully Free Version)")

# Load API keys from Streamlit secrets
ASSEMBLY_API_KEY = st.secrets["assembly_key"]
GROQ_API_KEY = st.secrets["groq_key"]

client = Groq(api_key=GROQ_API_KEY)

uploaded_file = st.file_uploader("Upload Audio or Video", type=["mp3", "wav", "m4a", "mp4"])

if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    st.info("Uploading to AssemblyAI...")

    headers = {"authorization": ASSEMBLY_API_KEY}

    # Upload file
    upload_url = "https://api.assemblyai.com/v2/upload"
    with open(temp_path, "rb") as f:
        upload_response = requests.post(upload_url, headers=headers, data=f)

    audio_url = upload_response.json()["upload_url"]

    # Request transcription
    transcript_request = {
        "audio_url": audio_url
    }

    transcript_response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json=transcript_request,
        headers=headers
    )

    transcript_id = transcript_response.json()["id"]

    # Poll for result
    status = "processing"
    while status != "completed":
        polling = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers=headers
        ).json()

        status = polling["status"]
        time.sleep(3)

    transcript = polling["text"]

    st.subheader(" Transcript")
    st.write(transcript)

    st.info("Generating study materials using Groq...")

    prompt = f"""
    From this lecture transcript:

    {transcript}

    Generate:
    1. A clean structured summary
    2. 5 quiz questions with answers
    3. 5 flashcards (Q/A format)
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )

    result = chat_completion.choices[0].message.content

    st.subheader(" Study Materials")
    st.write(result)