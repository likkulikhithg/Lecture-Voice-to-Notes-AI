import whisper
from transformers import pipeline

whisper_model = whisper.load_model("tiny")

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

def speech_to_text(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

def generate_notes(text):
    summary = summarizer(text, max_length=200, min_length=50, do_sample=False)
    return summary[0]["summary_text"]

def generate_quiz(text):
    sentences = text.split(".")
    quiz = ""
    for i, s in enumerate(sentences[:5]):
        quiz += f"Q{i+1}: Explain: {s.strip()}?\n\n"
    return quiz

def generate_flashcards(text):
    sentences = text.split(".")
    cards = ""
    for i, s in enumerate(sentences[:5]):
        cards += f"Flashcard {i+1}\nFront: {s.strip()}\nBack: Explanation.\n\n"
    return cards