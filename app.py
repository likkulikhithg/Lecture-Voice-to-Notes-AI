from flask import Flask, render_template, request
import os
from utils import speech_to_text, generate_notes, generate_quiz, generate_flashcards

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    notes = ""
    quiz = ""
    flashcards = ""

    if request.method == "POST":
        file = request.files["audio"]

        if file:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)

            transcript = speech_to_text(path)
            notes = generate_notes(transcript)
            quiz = generate_quiz(transcript)
            flashcards = generate_flashcards(transcript)

    return render_template(
        "index.html",
        transcript=transcript,
        notes=notes,
        quiz=quiz,
        flashcards=flashcards
    )

if __name__ == "__main__":
    app.run(debug=True)