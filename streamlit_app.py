import streamlit as st
import requests
import time
from groq import Groq
import tempfile

st.set_page_config(page_title="Lecture Voice-to-Notes AI")

st.title("Lecture Voice-to-Notes AI (Fully Free Version)")
st.write("Upload audio or video and generate transcript, summary, quiz, and flashcards.")

# Load API keys from Streamlit secrets
ASSEMBLY_API_KEY = st.secrets["assembly_key"]
GROQ_API_KEY = st.secrets["groq_key"]

client = Groq(api_key=GROQ_API_KEY)

uploaded_file = st.file_uploader(
    "Upload Audio or Video",
    type=["mp3", "wav", "m4a", "mp4"]
)

if uploaded_file:

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    st.info("Uploading to AssemblyAI...")

    headers = {"authorization": ASSEMBLY_API_KEY}

    # Upload file to AssemblyAI
    upload_url = "https://api.assemblyai.com/v2/upload"
    with open(temp_path, "rb") as f:
        upload_response = requests.post(
            upload_url,
            headers=headers,
            data=f
        )

    upload_json = upload_response.json()

    if "upload_url" not in upload_json:
        st.error("Upload Error")
        st.write(upload_json)
        st.stop()

    audio_url = upload_json["upload_url"]

    # Request transcription
    transcript_request = {
        "audio_url": audio_url,
        "speech_models": ["universal-2"]
    }

    transcript_response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json=transcript_request,
        headers=headers
    )

    response_json = transcript_response.json()

    if "id" not in response_json:
        st.error("AssemblyAI Error")
        st.write(response_json)
        st.stop()

    transcript_id = response_json["id"]

    # Poll for transcription completion
    status = "processing"

    while status not in ["completed", "error"]:
        polling = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers=headers
        ).json()

        status = polling["status"]
        time.sleep(3)

    if status == "error":
        st.error("Transcription Failed")
        st.write(polling)
        st.stop()

    transcript = polling["text"]

    st.subheader("Transcript")
    st.write(transcript)

    st.info("Generating study materials using Groq...")

    # Limit transcript size to prevent token overflow
    short_transcript = transcript[:6000]

    prompt = f"""
From this lecture transcript:

{short_transcript}

Generate:
1. A clean structured summary
2. 5 quiz questions with answers
3. 5 flashcards (Q/A format)
"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
        )
    except Exception as e:
        st.error("Groq Error")
        st.write(str(e))
        st.stop()

    result = chat_completion.choices[0].message.content

    st.subheader("Study Materials")
    st.write(result)