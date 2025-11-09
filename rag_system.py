import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

class RAGSystem:
    def __init__(self):
        print("\n🚀 Initializing RAG System...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.knowledge_base = []
        self.embeddings = None
        self.data_dir = Path(__file__).parent / "data"
        print("✅ SentenceTransformer loaded\n")

    def load_data(self):
        """Load all knowledge sources from JSON files"""
        print("="*70)
        print("📚 LOADING KNOWLEDGE BASE")
        print("="*70)
        
        # 1. Load questions_bank.json (LIST of questions)
        print("\n📖 Loading questions_bank.json...")
        questions_file = self.data_dir / "questions_bank.json"
        
        if questions_file.exists():
            with open(questions_file, "r", encoding="utf-8") as f:
                questions = json.load(f)
            
            if isinstance(questions, list):
                for q in questions:
                    self.knowledge_base.append({
                        "text": q.get("question", ""),
                        "field": q.get("field", "general"),
                        "category": "question",
                        "skills": q.get("skills", []),
                        "difficulty": q.get("difficulty", "medium")
                    })
                print(f"   ✅ Loaded {len(questions)} questions")
                print(f"      Fields: {set([q.get('field') for q in questions])}")
            else:
                print(f"   ❌ ERROR: questions_bank.json is not a list!")
        else:
            print(f"   ❌ ERROR: File not found: {questions_file}")

        # 2. Load job_roles.json (DICT of roles)
        print("\n📖 Loading job_roles.json...")
        roles_file = self.data_dir / "job_roles.json"
        
        if roles_file.exists():
            with open(roles_file, "r", encoding="utf-8") as f:
                job_roles = json.load(f)
            
            if isinstance(job_roles, dict):
                for role_name, role_data in job_roles.items():
                    desc = role_data.get('description', '')
                    skills = ', '.join(role_data.get('skills', []))
                    keywords = ', '.join(role_data.get('keywords', []))
                    
                    self.knowledge_base.append({
                        "text": f"{role_name}: {desc} Skills: {skills} Keywords: {keywords}",
                        "field": role_name.lower().replace(" ", "_"),
                        "category": "job_role",
                        "role_name": role_name
                    })
                print(f"   ✅ Loaded {len(job_roles)} job roles")
                print(f"      Roles: {list(job_roles.keys())}")
            else:
                print(f"   ❌ ERROR: job_roles.json is not a dict!")
        else:
            print(f"   ❌ ERROR: File not found: {roles_file}")

        # 3. Load interview_guidelines.json (LIST of guidelines)
        print("\n📖 Loading interview_guidelines.json...")
        guidelines_file = self.data_dir / "interview_guidelines.json"
        
        if guidelines_file.exists():
            with open(guidelines_file, "r", encoding="utf-8") as f:
                guidelines = json.load(f)
            
            if isinstance(guidelines, list):
                for g in guidelines:
                    self.knowledge_base.append({
                        "text": g.get("content", ""),
                        "category": g.get("category", "guideline"),
                        "weight": g.get("weight", 0.1)
                    })
                print(f"   ✅ Loaded {len(guidelines)} guidelines")
            else:
                print(f"   ❌ ERROR: interview_guidelines.json is not a list!")
        else:
            print(f"   ❌ ERROR: File not found: {guidelines_file}")

        # 4. Create embeddings
        if self.knowledge_base:
            print("\n🧠 Creating embeddings...")
            texts = [item.get("text", "") for item in self.knowledge_base]
            self.embeddings = self.model.encode(texts, convert_to_tensor=True)
            print(f"   ✅ Created {len(self.embeddings)} embeddings")
        else:
            print(f"   ❌ ERROR: Knowledge base is empty!")

        print("\n" + "="*70)
        print(f"✅ KNOWLEDGE BASE LOADED: {len(self.knowledge_base)} items total")
        print("="*70 + "\n")

    def retrieve(self, query, top_k=5):
        """Retrieve relevant documents from knowledge base"""
        if self.embeddings is None:
            print("❌ ERROR: Embeddings not initialized!")
            return []
        
        print(f"\n🔍 RETRIEVING: '{query[:80]}...'")
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.embeddings, top_k=top_k)[0]
        
        results = []
        for i, hit in enumerate(hits, 1):
            idx = hit['corpus_id']
            score = hit['score']
            result = self.knowledge_base[idx]
            results.append(result)
            print(f"   {i}. (score: {score:.3f}) {result.get('text', '')[:70]}...")
        
        return results

    def generate_questions(self, resume, job_role, num_questions=12):
        """Generate interview questions using RAG + Gemini"""
        
        print("\n" + "="*70)
        print(f"🎯 GENERATING QUESTIONS")
        print("="*70)
        print(f"Job Role: {job_role}")
        print(f"Resume Length: {len(resume)} characters")
        
        # Step 1: Retrieve relevant context
        print(f"\n📚 STEP 1: Retrieving context...")
        retrieved = self.retrieve(
            query=f"{job_role} interview questions {resume[:300]}",
            top_k=8
        )
        
        if not retrieved:
            print("⚠️  No context retrieved, using generic context")
            context = f"The role is {job_role}. Generate relevant technical and behavioral questions."
        else:
            # Filter to get question samples
            question_samples = [r.get('text', '') for r in retrieved if r.get('category') == 'question'][:5]
            role_info = [r.get('text', '') for r in retrieved if r.get('category') == 'job_role'][:2]
            
            context = f"""
SIMILAR QUESTIONS:
{chr(10).join([f'• {q}' for q in question_samples])}

ROLE INFORMATION:
{chr(10).join([f'• {r}' for r in role_info])}
"""
        
        print(f"✅ Retrieved {len(retrieved)} items")

        # Step 2: Create prompt
        print(f"\n🤖 STEP 2: Creating prompt...")
        prompt = f"""You are an expert HR interviewer for the role: {job_role}

CANDIDATE RESUME:
{resume}

CONTEXT FROM KNOWLEDGE BASE:
{context}

TASK:
Generate exactly {num_questions} unique interview questions tailored to this {job_role} candidate.

REQUIREMENTS:
1. Mix of question types:
   - 50% Technical questions (test skills and knowledge)
   - 30% Behavioral questions (use STAR method)
   - 20% Situational questions (problem-solving)

2. Vary difficulty levels:
   - 20% Easy (warm-up)
   - 60% Medium (core skills)
   - 20% Hard (advanced)

3. Be specific to the candidate's resume
4. Make questions unique and not generic
5. Do NOT repeat any questions

CRITICAL: Output ONLY a numbered list of questions, nothing else.
Format example:
1. What is your experience with [specific technology]?
2. Can you describe a time when you had to...
3. How would you approach...

Generate the {num_questions} questions NOW:
"""

        print("✅ Prompt created")

        # Step 3: Call Gemini
        print(f"\n🚀 STEP 3: Calling Gemini API...")
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt)
            
            print("✅ Gemini response received")
            
            # Step 4: Parse questions
            print(f"\n📝 STEP 4: Parsing questions...")
            questions = []
            
            for line in response.text.strip().split("\n"):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Remove numbering: "1.", "1)", "1-", "• ", etc.
                cleaned = line
                # Remove leading numbers and punctuation
                import re
                cleaned = re.sub(r'^[\d.)\-•\s]+', '', cleaned).strip()
                
                # Only keep meaningful questions (at least 10 chars, ends with ?)
                if len(cleaned) > 10 and (cleaned.endswith('?') or cleaned.endswith('.')):
                    questions.append(cleaned)
                    print(f"   ✅ Q{len(questions)}: {cleaned[:70]}...")
            
            print(f"\n" + "="*70)
            print(f"✅ GENERATED {len(questions)} QUESTIONS")
            print("="*70 + "\n")
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"\n❌ ERROR calling Gemini: {e}")
            import traceback
            traceback.print_exc()
            return []