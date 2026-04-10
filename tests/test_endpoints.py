import io
import pytest
from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_generate_quiz_endpoint():
    # Simulate a dummy PDF file upload
    # Since pypdf requires a valid PDF structure, we will mock the PdfReader in the API 
    # OR we can just pass a small valid dummy file.
    # The simplest is to send a dummy bytes payload and hope our mock handles it.
    dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n"
    
    response = client.post(
        "/api/generate", 
        files={"file": ("dummy.pdf", io.BytesIO(dummy_pdf_content), "application/pdf")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert "extracted_text" in data
    assert len(data["questions"]) > 0

def test_evaluate_answer_endpoint():
    payload = {
        "question": "What is photosynthesis?",
        "user_answer": "It is when plants eat soil.",
        "correct_answer": "It is the process used by plants to harness energy from sunlight.",
        "context_text": "Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy."
    }
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "is_correct" in data
    assert "reasoning" in data
    # Mock behavior should say it's incorrect based on context
    assert data["is_correct"] is False
