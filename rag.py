# simple_rag.py - Basic RAG System (Easy to Understand)
"""
RAG = Retrieval Augmented Generation
Step 1: Store documents in vector database
Step 2: When user asks question, find relevant documents
Step 3: Give documents to LLM as context
Step 4: LLM generates better answer using that context
"""

import json
import random
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from config import *

class BasicRAG:
    def __init__(self):
        """Initialize the RAG system"""
        print("\n🚀 Starting Basic RAG System...")
        
        # STEP 1: Load the embedding model (converts text to numbers)
        print("📥 Loading embedding model...")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✅ Loaded: {EMBEDDING_MODEL}")
        
        # STEP 2: Initialize vector database
        print("💾 Setting up vector database...")
        self.client = chromadb.Client()  # In-memory database (simple!)
        
        # Create a collection (like a table in SQL)
        try:
            self.collection = self.client.create_collection(
                name="interview_questions"
            )
            print("✅ Created new collection")
        except:
            self.collection = self.client.get_collection("interview_questions")
            print("✅ Using existing collection")
        
        # STEP 3: Connect to Gemini LLM
        print("🤖 Connecting to Gemini...")
        genai.configure(api_key=GEMINI_API_KEY)
        self.llm = genai.GenerativeModel(GEMINI_MODEL)
        print(f"✅ Connected to {GEMINI_MODEL}")
        
        print("✅ RAG System Ready!\n")
    
    def load_questions(self, filepath="data/questions.json"):
        """
        Load questions from JSON file into vector database
        This is like 'training' the RAG system
        """
        print(f"📚 Loading questions from {filepath}...")
        
        # Read JSON file
        with open(filepath, 'r') as f:
            questions_data = json.load(f)
        
        # Prepare data for ChromaDB
        documents = []  # The actual text
        metadatas = []  # Extra info about each document
        ids = []        # Unique ID for each document
        
        for i, item in enumerate(questions_data):
            documents.append(item['text'])
            metadatas.append({
                'role': item.get('role', 'general'),
                'type': item.get('type', 'general')
            })
            ids.append(f"q_{i}")
        
        # Add to vector database
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ Loaded {len(documents)} questions into RAG system\n")
        
        return len(documents)
    
    def search(self, query, top_k=TOP_K):
        """
        Search for relevant questions in vector database
        This is the 'Retrieval' part of RAG
        """
        print(f"🔍 Searching for: '{query[:50]}...'")
        
        # Query the vector database
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format the results nicely
        retrieved = []
        if results['documents'][0]:
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                retrieved.append({
                    'text': doc,
                    'role': metadata['role'],
                    'type': metadata['type'],
                    'similarity': 1 - distance  # Convert distance to similarity score
                })
            
            print(f"✅ Found {len(retrieved)} relevant questions")
        else:
            print("⚠️ No results found")
        
        return retrieved
    
    def generate_questions(self, resume, job_role, num_questions=None):
        """
        Generate interview questions using RAG
        This is the 'Augmented Generation' part
        """
        if num_questions is None:
            num_questions = random.randint(MIN_QUESTIONS, MAX_QUESTIONS)
        
        print(f"\n{'='*60}")
        print(f"🎯 Generating {num_questions} questions for {job_role}")
        print(f"{'='*60}")
        
        # STEP 1: RETRIEVE relevant questions from vector DB
        search_query = f"{job_role} interview questions for candidate with: {resume[:200]}"
        retrieved_questions = self.search(search_query, top_k=8)
        
        # Build context from retrieved questions
        context = "Here are similar questions used in past interviews:\n"
        for i, q in enumerate(retrieved_questions[:5], 1):
            context += f"{i}. {q['text']}\n"
        
        # STEP 2: AUGMENT the prompt with retrieved context
        prompt = f"""
You are an expert HR interviewer.

**Retrieved Context (Similar questions from past interviews):**
{context}

**Candidate's Resume:**
{resume}

**Job Role:** {job_role}

**Instructions:**
1. Use the retrieved questions as inspiration (but don't copy them exactly)
2. Create {num_questions} NEW questions tailored to this candidate
3. Mix technical and behavioral questions
4. Make questions specific to their experience

Return ONLY a JSON array of strings:
["Question 1?", "Question 2?", ...]
"""
        
        # STEP 3: GENERATE with LLM
        print("🤖 Generating with RAG...")
        try:
            response = self.llm.generate_content(prompt)
            questions = json.loads(
                response.text.replace("```json", "").replace("```", "").strip()
            )
            print(f"✅ Generated {len(questions)} questions")
            print(f"{'='*60}\n")
            return questions
        
        except Exception as e:
            print(f"❌ Error: {e}")
            # Fallback: return retrieved questions
            return [q['text'] for q in retrieved_questions[:num_questions]]
    
    def get_stats(self):
        """Get statistics about the RAG system"""
        count = self.collection.count()
        return {
            "total_questions": count,
            "embedding_model": EMBEDDING_MODEL,
            "llm_model": GEMINI_MODEL
        }


# ============================================
# TEST THE RAG SYSTEM (Run this file directly)
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING BASIC RAG SYSTEM")
    print("="*60)
    
    # 1. Initialize RAG
    rag = BasicRAG()
    
    # 2. Load questions
    rag.load_questions()
    
    # 3. Test search
    print("\n--- TEST 1: Search ---")
    results = rag.search("Python programming experience", top_k=3)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['text'][:60]}... (similarity: {r['similarity']:.2f})")
    
    # 4. Test question generation
    print("\n--- TEST 2: Generate Questions ---")
    test_resume = "Software engineer with 3 years Python experience. Worked on Django and Flask projects."
    questions = rag.generate_questions(
        resume=test_resume,
        job_role="Python Developer",
        num_questions=5
    )
    
    print("\nGenerated Questions:")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
    
    # 5. Show stats
    print(f"\n--- Stats ---")
    stats = rag.get_stats()
    print(f"📊 {stats}")
    
    print("\n✅ RAG System Test Complete!")