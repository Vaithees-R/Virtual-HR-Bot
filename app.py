from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_system import RAGSystem
from resume_extractor import extract_resume_text
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

app = Flask(__name__)
CORS(app)  # ✅ Allow UI to talk with Flask (important if using frontend)

# Initialize RAG system
rag = RAGSystem()
rag.load_data()  # ✅ correct
  # ✅ Your existing RAG init

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)


# 🧠 Route 1 — Generate Questions (if resume text already provided)
@app.route("/generate-questions", methods=["POST"])
def generate_questions():
    try:
        data = request.json
        resume = data.get("resume_text", "")
        job_role = data.get("job_role", "")

        if not resume or not job_role:
            return jsonify({"error": "Missing resume_text or job_role"}), 400

        retrieved = rag.retrieve(f"{job_role} interview questions {resume}", top_k=5)
        context = "\n".join([r.get("text", "") for r in retrieved])


        prompt = f"""
        You are an HR interviewer for a {job_role} role.
        Use the following retrieved context to generate 10 relevant interview questions.

        ### Context:
        {context}

        ### Instructions:
        - Focus on technical and behavioral questions.
        - Make them specific to this candidate's resume.
        - Output only a list of questions (no explanations).
        """

        response = model.generate_content(prompt)
        questions = [q.strip("•-1234567890. ") for q in response.text.strip().split("\n") if q.strip()]
        questions = [q for q in questions if len(q) > 5]

        return jsonify({
            "success": True,
            "job_role": job_role,
            "total_questions": len(questions),
            "questions": questions
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📄 Route 2 — Upload Resume + Auto Extract Text + Generate Questions
@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    try:
        file = request.files.get("resume")
        job_role = request.form.get("job_role", "")

        if not file:
            return jsonify({"error": "No resume file uploaded"}), 400
        if not job_role:
            return jsonify({"error": "Missing job_role"}), 400

        # Save temporarily
        save_path = f"temp_{file.filename}"
        file.save(save_path)

        # Extract text from resume
        resume_text = extract_resume_text(save_path)

        # Delete temp file
        import os
        os.remove(save_path)

        print("\n🧠 Extracted Resume Content (Preview):")
        print(resume_text[:400], "...")

        # Generate questions using RAG + Gemini
        questions = rag.generate_questions(resume=resume_text, job_role=job_role)

        return jsonify({
        "success": True,
        "job_role": job_role,
        "total_questions": len(questions),
        "questions": questions,
        "resume_text_preview": resume_text[:400],
        "metadata": {
        "candidate_name": job_role,  # or extract from resume
        "words": len(resume_text.split())
        }
    }), 200


    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n🚀 Running Full AI HR Interview System (with Resume Upload)...")
    app.run(host="127.0.0.1", port=5000, debug=True)
