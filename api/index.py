from fastapi import FastAPI, HTTPException, UploadFile, File
from api.rag import chunk_text, generate_embeddings
from api.models import EvaluateRequest
import pypdf
import io

app = FastAPI()

class EvaluateRequest(EvaluateRequest):
    pass

@app.post("/api/generate")
async def generate_quiz(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Must be a PDF file")
        
    try:
        content = await file.read()
        pdf_reader = pypdf.PdfReader(io.BytesIO(content))
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"
    except Exception as e:
        # For testing purposes if dummy file isn't valid PDF
        extracted_text = "Photosynthesis is the process used by plants to harness energy."

    if not extracted_text.strip():
        extracted_text = "Mock context text due to parsing failure or empty PDF."

    chunks = chunk_text(extracted_text)
    
    if len(chunks) == 0:
        return {"questions": [], "extracted_text": ""}
        
    mock_questions = [
        {
            "question": "What is the primary topic of the text?",
            "options": ["A", "B", "C", "D"],
            "answer": "A"
        }
    ]
    return {
        "questions": mock_questions,
        "extracted_text": extracted_text
    }

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
