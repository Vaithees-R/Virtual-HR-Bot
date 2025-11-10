# rag_system.py
import json
from sentence_transformers import SentenceTransformer, util

class RAGSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.knowledge_base = []
        self.embeddings = None

    def load_data(self):
        # Load all your sources
        with open("D:\V_HR_BOT\VHB\data\question_bank.json", "r", encoding="utf-8") as f:
            questions = json.load(f)
        with open("D:\V_HR_BOT\VHB\data\job_roles.json", "r", encoding="utf-8") as f:
            job_roles = json.load(f)
        with open("D:\V_HR_BOT\VHB\data\interview_guidelines.json", "r", encoding="utf-8") as f:
            guidelines = json.load(f)

        # Combine into one knowledge base
        for role, details in job_roles.items():
            self.knowledge_base.append({
                "text": f"{role}: {details['description']} Skills: {', '.join(details['skills'])}",
                "category": "job_role"
            })

        for q in questions:
            self.knowledge_base.append({
                "text": q["question"],
                "category": "question_bank"
            })

        for g in guidelines:
            self.knowledge_base.append({
                "text": g["content"],
                "category": "guideline"
            })

        # Create embeddings
        texts = [item["text"] for item in self.knowledge_base]
        self.embeddings = self.model.encode(texts, convert_to_tensor=True)
        print(f"✅ Loaded {len(self.knowledge_base)} items into RAG knowledge base.")

    def retrieve(self, query, top_k=5):
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.embeddings, top_k=top_k)[0]
        return [self.knowledge_base[hit['corpus_id']] for hit in hits]

    def generate_questions(self, resume, job_role, top_k=5):
        """Generate interview questions using RAG and Gemini"""
        import google.generativeai as genai
        from config import GEMINI_API_KEY, GEMINI_MODEL

        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Step 1: Retrieve related context from the knowledge base
        retrieved = self.retrieve(f"{job_role} interview questions {resume}", top_k=top_k)
        context = "\n".join([r["text"] for r in retrieved])

        # Step 2: Create prompt for Gemini
        prompt = f"""
        You are an HR interviewer for a {job_role} role.
        Use the following retrieved context to generate 10 relevant interview questions.

        ### Context:
        {context}

        ### Instructions:
        - Include both technical and behavioral questions.
        - Make them specific to the candidate's resume.
        - Output only a numbered list of questions (no explanations).
        """

        # Step 3: Generate content
        response = model.generate_content(prompt)
        questions = [
            q.strip("•-1234567890. ")
            for q in response.text.strip().split("\n")
            if q.strip()
        ]
        return [q for q in questions if len(q) > 5]