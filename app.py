from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_system import RAGSystem
from resume_extractor import extract_resume_text
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
import re, traceback, os

app = Flask(__name__)
CORS(app)

# Initialize RAG & Gemini
rag = RAGSystem()
rag.load_data()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# ======================================================
# 📄 ROUTE 1: Upload Resume → Extract + Generate Questions
# ======================================================
@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    try:
        file = request.files.get("resume")
        job_role = request.form.get("job_role", "")
        candidate_name = request.form.get("candidate_name", "Candidate")

        if not file:
            return jsonify({"error": "No resume file uploaded"}), 400
        if not job_role:
            return jsonify({"error": "Missing job_role"}), 400

        temp_path = f"temp_{file.filename}"
        file.save(temp_path)
        resume_text = extract_resume_text(temp_path)
        os.remove(temp_path)

        # Generate questions using RAG + Gemini
        questions = rag.generate_questions(resume=resume_text, job_role=job_role)

        return jsonify({
            "success": True,
            "candidate_name": candidate_name,
            "job_role": job_role,
            "questions": questions,
            "total_questions": len(questions),
            "resume_text_preview": resume_text[:400]
        }), 200

    except Exception as e:
        print("❌ Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# ======================================================
# 🎤 ROUTE 2: Evaluate Answer (candidate’s STT text)
# ======================================================
@app.route("/evaluate-answer", methods=["POST"])
def evaluate_answer():
    try:
        data = request.get_json(force=True)
        question = data.get("question", "")
        answer = data.get("answer", "")
        job_role = data.get("job_role", "")

        if not question or not answer:
            return jsonify({"error": "Missing question or answer"}), 400

        prompt = f"""
        You are an AI HR interviewer evaluating a spoken answer for the role of {job_role}.
        Question: "{question}"
        Candidate's Answer: "{answer}"

        Please rate from 1 to 10 for:
        - Relevance
        - Technical accuracy
        - Clarity
        - Confidence

        Provide a short feedback and an overall score.
        """

        response = model.generate_content(prompt)
        feedback = response.text.strip()
        score_match = re.search(r"\b([0-9]|10)\b", feedback)
        score = score_match.group(1) if score_match else "N/A"

        return jsonify({
            "success": True,
            "feedback": feedback,
            "score": score
        }), 200

    except Exception as e:
        print("❌ Evaluation Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# ======================================================
# 🚀 MAIN ENTRY
# ======================================================
if __name__ == "__main__":
    print("✅ RAG Knowledge Base Loaded")
    print("🚀 Running Full AI HR Interviewer...")
    app.run(host="127.0.0.1", port=5000, debug=True)
