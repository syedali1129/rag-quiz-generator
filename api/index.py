from fastapi import FastAPI, HTTPException
from api.rag import chunk_text, generate_embeddings
from api.models import GenerateRequest, EvaluateRequest

app = FastAPI()

@app.post("/api/generate")
def generate_quiz(request: GenerateRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    # In a real implementation with LLMs, we would:
    # 1. Chunk the text
    # 2. Provide the text to OpenAI/Gemini
    # 3. Request JSON output with Q&A pairs
    
    # Mocking implementation for tests since no API key is provided yet
    chunks = chunk_text(request.text)
    
    if len(chunks) == 0:
        return {"questions": []}
        
    mock_questions = [
        {
            "question": "What is the primary topic of the text?",
            "options": ["A", "B", "C", "D"],
            "answer": "A"
        }
    ]
    return {"questions": mock_questions}

@app.post("/api/evaluate")
def evaluate_answer(request: EvaluateRequest):
    # Real implementation uses the LLM to compare user_answer with correct_answer contextually.
    is_correct = request.user_answer.strip().lower() == request.correct_answer.strip().lower()
    
    reasoning = ""
    if not is_correct:
        # Here we would do a RAG lookup on context_text 
        # and ask the LLM to explain why the user was wrong
        reasoning = f"Mock Reasoning: The correct answer highlights energy from sunlight, whereas you answered: '{request.user_answer}'. Let's review the knowledge base."
        
    return {
        "is_correct": is_correct,
        "reasoning": reasoning
    }
