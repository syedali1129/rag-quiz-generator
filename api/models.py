from pydantic import BaseModel

class GenerateRequest(BaseModel):
    text: str

class EvaluateRequest(BaseModel):
    question: str
    user_answer: str
    correct_answer: str
    context_text: str
