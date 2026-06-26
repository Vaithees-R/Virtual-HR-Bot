# 🤖 V-HR Bot — AI-Powered Interview System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-FF6B35?style=for-the-badge)
![LangChain](https://img.shields.io/badge/RAG_Pipeline-Sentence_Transformers-brightgreen?style=for-the-badge)

**An intelligent HR interview bot that reads a candidate's resume, generates tailored interview questions using RAG, and evaluates spoken responses — all via a REST API.**

</div>

---

## 📌 What It Does

1. **Resume Ingestion** — Accepts PDF, DOCX, PNG/JPG (OCR), or TXT resumes and extracts clean text
2. **RAG-Powered Question Generation** — Retrieves semantically similar questions from a curated 1,000-question bank and augments Gemini prompts with them
3. **Answer Evaluation** — Scores candidate answers across Relevance, Technical Accuracy, Clarity, and Confidence
4. **REST API** — Full Flask backend, CORS-enabled, ready to connect to any frontend

---

## 🗂️ Project Structure

```
HR_BOT/
├── app.py                  # Flask API entry point
├── config.py               # Model config, paths, retrieval settings
├── rag.py                  # BasicRAG — simple in-memory ChromaDB RAG
├── rag_system.py           # RAGSystem — full knowledge base with job roles & guidelines
├── interviewer.py          # Fallback interviewer (no RAG, direct Gemini)
├── resume_extractor.py     # PDF / DOCX / Image text extraction
├── resume_processor.py     # Metadata-aware resume processor
├── utils.py                # File upload handler (PyMuPDF + OCR)
├── requirements.txt
├── data/
│   ├── job_roles.json
│   ├── question_bank.json
│   └── interview_guidelines.json
├── datasets/
│   ├── resumes/
│   ├── questions/
│   └── feedback/
└── vector_db/              # ChromaDB persistent store (auto-created)
```

---

## 🧠 Question Bank

**1,000 questions across 10 professional roles:**

| Role | Technical | Behavioral | Situational | General |
|---|---|---|---|---|
| Python Developer | 50 | 30 | 20 | 10 |
| Frontend Developer | 50 | 30 | 20 | 10 |
| Backend Developer | 50 | 30 | 20 | 10 |
| DevOps Engineer | 50 | 30 | 20 | 10 |
| Data Scientist | 50 | 30 | 20 | 10 |
| MLOps Engineer | 50 | 30 | 20 | 10 |
| QA / Test Engineer | 50 | 30 | 20 | 10 |
| System Architect | 50 | 30 | 20 | 10 |
| Cloud Engineer | 50 | 30 | 20 | 10 |
| Full Stack Developer | 50 | 30 | 20 | 10 |

---

## ⚙️ Setup

### 1. Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows — download from:
# https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. Clone & Install

```bash
git clone https://github.com/Vaithees-R/hr-bot-interviewer.git
cd hr-bot-interviewer

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
DEBUG_MODE=True
```

> ⚠️ Never commit your `.env` file. It is already in `.gitignore`.

### 4. Run

```bash
python app.py
```

Server starts at `http://127.0.0.1:5000`

---

## 🔌 API Endpoints

### `POST /upload-resume`
Upload a resume file and generate tailored interview questions.

```bash
curl -X POST \
  -F "resume=@resume.pdf" \
  -F "job_role=Python Developer" \
  -F "candidate_name=John Doe" \
  http://127.0.0.1:5000/upload-resume
```

**Response:**
```json
{
  "success": true,
  "candidate_name": "John Doe",
  "job_role": "Python Developer",
  "questions": ["Question 1?", "Question 2?", "..."],
  "total_questions": 10,
  "resume_text_preview": "..."
}
```

---

### `POST /evaluate-answer`
Evaluate a candidate's spoken/typed answer.

```bash
curl -X POST http://127.0.0.1:5000/evaluate-answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain how you would design a REST API.",
    "answer": "I would start by defining the resources...",
    "job_role": "Backend Developer"
  }'
```

**Response:**
```json
{
  "success": true,
  "feedback": "Strong technical understanding. Covered key REST principles...",
  "score": "8"
}
```

---

## 🔁 RAG Pipeline

```
Resume + Job Role
       │
       ▼
  Semantic Search  ←──  ChromaDB (1000 questions embedded with all-MiniLM-L6-v2)
       │
       ▼
  Top-K Retrieved Questions
       │
       ▼
  Augmented Prompt  ──►  Gemini 2.5 Flash
       │
       ▼
  Tailored Interview Questions
```

The system uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings and ChromaDB as the vector store. Gemini is used only for generation — retrieval is fully local.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `flask` | REST API server |
| `flask-cors` | Cross-origin support |
| `google-generativeai` | Gemini 2.5 Flash LLM |
| `chromadb` | Vector database |
| `sentence-transformers` | Text embeddings (MiniLM) |
| `PyPDF2` / `PyMuPDF` | PDF text extraction |
| `pytesseract` + `Pillow` | OCR for image resumes |
| `python-docx` | DOCX extraction |

---

## 🛠️ Troubleshooting

```bash
# Verify core installs
python -c "import PyPDF2; print('✓ PyPDF2')"
python -c "import pytesseract; print('✓ pytesseract')"
python -c "import chromadb; print('✓ ChromaDB')"
python -c "import flask; print('✓ Flask')"

# Kill port 5000 if already in use
lsof -ti:5000 | xargs kill -9

# Reset vector DB
rm -rf vector_db/chromadb
```

---

## 🚀 Roadmap

- [ ] Frontend UI (React / Vanilla JS)
- [ ] Speech-to-text integration for live interview mode
- [ ] Per-role difficulty scoring
- [ ] Export interview report as PDF
- [ ] Docker containerization

---

## 👤 Author

**Vaithees R**  
B.Sc. AI & ML | Junior ML Engineer  
📧 vaithees.r12@gmail.com  
🔗 [github.com/Vaithees-R](https://github.com/Vaithees-R)

---

<div align="center">
<sub>Built with Python · Flask · ChromaDB · Gemini · Sentence Transformers</sub>
</div>
