from fastapi import FastAPI, HTTPException, UploadFile, File
from api.rag import chunk_text, generate_embeddings
from api.models import EvaluateRequest
import pypdf
import io
import os
import json
from groq import Groq

app = FastAPI()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "dummy"))

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
        extracted_text = "Photosynthesis is the process used by plants to harness energy."

    if not extracted_text.strip():
        extracted_text = "Mock context text due to parsing failure or empty PDF."

    # Prevent exceeding Groq's strict free-tier TPM (Tokens Per Minute) limit (6000 tokens)
    # 1 token is roughly 4 characters. We slice at 12,000 characters (~3000 tokens) to ensure maximum safety.
    safe_text_context = extracted_text[:12000]

    # Prompt Groq!
    prompt = f"""
    You are a highly intelligent educational assistant. 
    Read the following text and generate exactly 5 multiple choice questions based on the content.
    Your response must be a highly structured JSON object with a single key 'questions' containing a list of dictionaries.
    Each dictionary must have:
    'question': the question text
    'options': a list of exactly 4 string options
    'answer': the exact string from 'options' that is correct
    
    Text Context:
    {safe_text_context}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You output strictly JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        llm_response = json.loads(chat_completion.choices[0].message.content)
        questions = llm_response.get("questions", [])
    except Exception as e:
        if "dummy" in os.environ.get("GROQ_API_KEY", "dummy"):
            questions = [{"question":"What is the primary topic of the text?","options":["A","B","C","D"],"answer":"A"}]
        else:
            raise HTTPException(status_code=500, detail=f"Groq API Error: {str(e)}")

    return {
        "questions": questions,
        "extracted_text": extracted_text
    }

@app.post("/api/evaluate")
def evaluate_answer(request: EvaluateRequest):
    is_correct = request.user_answer.strip().lower() == request.correct_answer.strip().lower()
    
    reasoning = ""
    if not is_correct:
        # Heavily truncate context to prevent evaluate queries from stacking against the Groq TPM limit
        safe_evaluate_context = request.context_text[:12000]
        
        prompt = f"""
        The user answered a question incorrectly.
        Question: {request.question}
        User's Answer: {request.user_answer}
        Correct Answer: {request.correct_answer}
        Look at the provided Context Text and explain briefly (1-2 sentences max) WHY the user's answer is wrong.
        
        Context Text:
        {safe_evaluate_context}
        """
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant"
            )
            reasoning = chat_completion.choices[0].message.content
        except Exception as e:
             reasoning = f"AI Reasoning unavailable. Ensure GROQ_API_KEY is placed in Vercel. Error details: {str(e)}"

    return {
        "is_correct": is_correct,
        "reasoning": reasoning
    }
