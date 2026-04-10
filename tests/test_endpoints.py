import pytest
from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_generate_quiz_endpoint():
    payload = {
        "text": "Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy."
    }
    response = client.post("/api/generate", json=payload)
    # We expect a mock response since we don't have API keys yet.
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) > 0
    assert "options" in data["questions"][0]

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
