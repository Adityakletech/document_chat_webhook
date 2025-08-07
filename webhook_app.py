from flask import Flask, request, jsonify
from openai import OpenAI
import pypdf
import docx2txt
import io
import os

# Initialize Flask app first!
app = Flask(__name__)

# Home route to verify deployment
@app.route("/", methods=["GET"])
def index():
    return "✅ Flask is running on Render!"

# Get API Key from environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-r1:free"

client = OpenAI(base_url=BASE_URL, api_key=OPENROUTER_API_KEY)

# --- Helper functions ---
def extract_pdf_text(file):
    pdf_reader = pypdf.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

def extract_txt_text(file):
    raw = file.read()
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="ignore")
    return raw

def extract_docx_text(file):
    try:
        file_bytes = io.BytesIO(file.read())
        text = docx2txt.process(file_bytes)
        return text.strip()
    except Exception:
        return ""

def extract_text(file, file_type):
    file_type = file_type.lower()
    if file_type == "application/pdf":
        return extract_pdf_text(file)
    elif file_type == "text/plain":
        return extract_txt_text(file)
    elif file_type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]:
        return extract_docx_text(file)
    else:
        return ""

def ask_llm(question, context_text):
    prompt = f"Answer the question based only on the context below.\n\nContext:\n{context_text[:6000]}\n\nQuestion: {question}"
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        question = request.form.get("question")
        if not question:
            return jsonify({"error": "Question is required"}), 400

        file = request.files.get("file")
        if not file:
            return jsonify({"error": "File is required"}), 400

        context_text = extract_text(file, file.content_type)
        if not context_text:
            return jsonify({"error": "Could not extract text"}), 400

        answer = ask_ll_
