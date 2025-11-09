# interviewer.py
"""
Fallback Interviewer Module (Without RAG)
Used when RAG is disabled or as backup
"""

import random
import json
import time
import google.generativeai as genai
from config import *

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

def generate_questions_simple(resume: str, job_role: str, 
                             num_questions: int = None) -> list:
    """
    Simple question generation without RAG
    Direct LLM call without retrieval
    """
    if num_questions is None:
        num_questions = random.randint(MIN_QUESTIONS, MAX_QUESTIONS)
    
    print(f"\n{'='*70}")
    print(f"📝 GENERATING {num_questions} QUESTIONS (Simple Mode - No RAG)")
    print(f"{'='*70}")
    
    prompt = f"""You are an expert HR interviewer.

**Candidate Resume:**
{resume}

**Job Role:** {job_role}

**Task:**
Generate exactly {num_questions} interview questions for this candidate.

**Requirements:**
- Mix technical, behavioral, and situational questions
- Tailor to the candidate's experience and the job role
- Make questions specific and insightful

**Output:**
Return ONLY a valid JSON array of strings.
Example: ["Question 1?", "Question 2?"]
"""
    
    try:
        response = model.generate_content(prompt)
        json_string = response.text.replace("```json", "").replace("```", "").strip()
        questions = json.loads(json_string)
        
        print(f"✅ Generated {len(questions)} questions")
        print("="*70 + "\n")
        return questions
        
    except Exception as e:
        print(f"⚠️ Error: {e}")
        # Fallback questions
        fallback = [
            f"Tell me about your background and why you're interested in the {job_role} position.",
            "Describe a challenging project you worked on. What was your role?",
            "How do you approach problem-solving when facing technical challenges?",
            "Tell me about a time you had to work under a tight deadline.",
            "What are your key technical skills and how have you applied them?",
            "Describe a situation where you had to learn something new quickly.",
            "How do you handle feedback and code reviews?",
            "What motivates you in your career and what are your goals?",
            "Tell me about a time you collaborated with a team to achieve a goal.",
            f"Why do you want to work as a {job_role} and what interests you about this role?"
        ]
        return fallback[:num_questions]

def evaluate_simple(interview_data: list) -> dict:
    """
    Simple evaluation without RAG
    Direct LLM call without retrieval
    """
    print(f"\n{'='*70}")
    print(f"📊 EVALUATING INTERVIEW (Simple Mode - No RAG)")
    print(f"{'='*70}")
    
    # Build transcript
    qa_text = ""
    answered_count = 0
    
    for i, item in enumerate(interview_data, 1):
        status = item.get('status', 'answered')
        if status == 'answered':
            qa_text += f"\nQ{i}: {item['question']}\nA{i}: {item['answer']}\n"
            answered_count += 1
        else:
            qa_text += f"\nQ{i}: {item['question']}\nA{i}: [SKIPPED]\n"
    
    print(f"   Answered: {answered_count}, Skipped: {len(interview_data) - answered_count}")
    
    prompt = f"""You are an expert HR evaluator.

**Interview Transcript:**
{qa_text}

**Task:**
Evaluate each answer and provide overall assessment.

**Scoring:**
- 5: Exceptional, 4: Strong, 3: Adequate, 2: Weak, 1: Poor, 0: Skipped

**Output:**
Return ONLY valid JSON:
{{
    "individual_scores": [
        {{"question_number": 1, "score": 4, "feedback": "Detailed feedback..."}},
        ...
    ],
    "overall_score": 4.2,
    "overall_feedback": "Summary of performance...",
    "strengths": ["Strength 1", "Strength 2"],
    "improvements": ["Improvement 1", "Improvement 2"]
}}
"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            json_string = response.text.replace("```json", "").replace("```", "").strip()
            evaluation = json.loads(json_string)
            
            print("✅ Evaluation completed")
            print("="*70 + "\n")
            return evaluation
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"   Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Error: {e}")
                return _create_fallback_evaluation(interview_data)
    
    return _create_fallback_evaluation(interview_data)

def _create_fallback_evaluation(interview_data: list) -> dict:
    """Create basic evaluation when API fails"""
    answered = sum(1 for item in interview_data if item.get('status') == 'answered')
    skipped = len(interview_data) - answered
    
    individual_scores = []
    total = 0
    
    for i, item in enumerate(interview_data, 1):
        if item.get('status') == 'skipped':
            individual_scores.append({
                "question_number": i,
                "score": 0,
                "feedback": "Question was skipped"
            })
        else:
            score = 3
            total += score
            individual_scores.append({
                "question_number": i,
                "score": score,
                "feedback": "Response recorded and reviewed"
            })
    
    avg = round(total / answered, 1) if answered > 0 else 0
    
    return {
        "individual_scores": individual_scores,
        "overall_score": avg,
        "overall_feedback": f"Interview completed with {answered} answers and {skipped} skipped.",
        "strengths": ["Completed the interview", "Provided responses"],
        "improvements": ["Provide more detailed answers", "Give specific examples"]
    }