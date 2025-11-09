from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_system import RAGSystem
from resume_processor import ResumeProcessor
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Initialize systems
print("\n" + "="*70)
print("⚙️  INITIALIZING SYSTEMS")
print("="*70)

print("\n1️⃣  Initializing RAG System...")
rag = RAGSystem()

print("\n2️⃣  Initializing Resume Processor...")
resume_processor = ResumeProcessor()

print("\n3️⃣  Loading RAG knowledge base...")
rag.load_data()

print("\n✅ ALL SYSTEMS READY!\n")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "rag_loaded": len(rag.knowledge_base) > 0,
        "knowledge_items": len(rag.knowledge_base),
        "message": "System is ready for interviews"
    }), 200


@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    """Upload resume file and generate questions"""
    try:
        print("\n" + "="*70)
        print("📥 UPLOAD-RESUME REQUEST")
        print("="*70)
        
        # Get file and job role
        file = request.files.get("resume")
        job_role = request.form.get("job_role", "").strip()
        candidate_name = request.form.get("candidate_name", "Candidate").strip()

        print(f"File: {file.filename if file else 'None'}")
        print(f"Job Role: {job_role}")
        print(f"Candidate: {candidate_name}")

        # Validate
        if not file:
            return jsonify({"error": "No resume file uploaded"}), 400
        if not job_role:
            return jsonify({"error": "Missing job_role parameter"}), 400

        # Process resume
        print(f"\n🔄 Processing resume file: {file.filename}")
        result = resume_processor.process_resume(file.stream, candidate_name)

        if not result['success']:
            error_msg = result.get('error', 'Failed to process resume')
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400

        resume_text = result['resume_text']
        metadata = result['metadata']
        
        print(f"✅ Extracted {metadata['words']} words from resume")

        # Generate questions
        print(f"\n🎯 Generating questions...")
        questions = rag.generate_questions(
            resume=resume_text,
            job_role=job_role,
            num_questions=12
        )

        if not questions:
            return jsonify({"error": "Failed to generate questions"}), 500

        print(f"\n✅ SUCCESS!")
        return jsonify({
            "success": True,
            "job_role": job_role,
            "candidate_name": candidate_name,
            "total_questions": len(questions),
            "questions": questions,
            "resume_preview": resume_text[:300],
            "metadata": metadata
        }), 200

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "details": traceback.format_exc()}), 500


@app.route("/generate-questions", methods=["POST"])
def generate_questions():
    """Generate questions from text resume"""
    try:
        print("\n" + "="*70)
        print("📝 GENERATE-QUESTIONS REQUEST")
        print("="*70)
        
        data = request.json or {}
        resume_text = data.get("resume_text", "").strip()
        job_role = data.get("job_role", "").strip()

        print(f"Job Role: {job_role}")
        print(f"Resume Length: {len(resume_text)} characters")

        # Validate
        if not resume_text:
            return jsonify({"error": "Missing resume_text"}), 400
        if not job_role:
            return jsonify({"error": "Missing job_role"}), 400

        # Generate questions
        print(f"\n🎯 Generating questions...")
        questions = rag.generate_questions(
            resume=resume_text,
            job_role=job_role,
            num_questions=12
        )

        if not questions:
            return jsonify({"error": "Failed to generate questions"}), 500

        print(f"\n✅ SUCCESS!")
        return jsonify({
            "success": True,
            "job_role": job_role,
            "total_questions": len(questions),
            "questions": questions
        }), 200

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 AI HR INTERVIEWER - STARTING SERVER")
    print("="*70)
    print(f"📍 URL: http://127.0.0.1:5000")
    print(f"🧪 Health Check: http://127.0.0.1:5000/health")
    print("="*70 + "\n")
    
    app.run(host="127.0.0.1", port=5000, debug=True)