# LearnRAG - AI Quiz Generator

LearnRAG is an intelligent, full-stack web application that allows users to upload educational PDF documents and instantly generates an interactive multiple-choice quiz based on the extracted context. Built with modern AI techniques, it utilizes Retrieval-Augmented Generation (RAG) principles to ensure questions are deeply grounded in the user's uploaded material, drastically reducing AI hallucinations.

## How It Works

1. **Ingestion**: The user uploads a PDF file. The backend reads and extracts text from the document using `pypdf`.
2. **Context Processing**: The extracted text is processed and intelligently chunked. A specialized chunking algorithm ensures semantic meaning is preserved across text bounds by using overlapping sentences.
3. **Quiz Generation**: The processed context is passed to the Groq API (running the `llama-3.1-8b-instant` model), which strictly generates 5 multiple-choice questions in a validated JSON format.
4. **Interactive Assessment**: The user takes the quiz on the frontend interface. 
5. **AI Evaluation**: Upon submission, the user's answers are verified against the correct answers. If a user gets a question wrong, the LLM provides immediate, natural-language reasoning explaining *why* they were wrong based strictly on the uploaded text.

## Architecture

This project adopts a lightweight, highly-performant serverless architecture.

### Frontend
- **Tech Stack**: Vanilla HTML, CSS, and JavaScript.
- **Design**: A sleek, single-page application (SPA) featuring glassmorphism and dynamic state transitions without requiring full page reloads.
- **Interaction**: Handles asynchronous `fetch` requests to the backend, dynamic DOM manipulation for quiz rendering, and state management for tracking the user's score and evaluation progress.

### Backend
- **Tech Stack**: FastAPI deployed as Serverless Functions on Vercel (`api/index.py`).
- **Data Pipeline**: Python-based endpoints process multipart file uploads, parse PDFs into raw text strings, and manage the structured communication with the Groq LLM API.
- **RAG Component (`api/rag.py`)**: Features a custom text chunking utility leveraging advanced regular expressions to prevent splitting on decimals or honorifics, whilst employing sentence-overlap to guarantee context isn't lost during vectorization or generation.

## Known Issues & Limitations

- **Groq Token Limits**: The free tier of the Groq API has a strict Tokens Per Minute (TPM) limit (approx. 6000 tokens). To prevent the backend from crashing when processing large PDFs, the text context is aggressively truncated to the first ~12,000 characters before being sent to the LLM. 
- **Sequential Evaluation**: Currently, during the evaluation phase, the frontend pings the backend sequentially for AI reasoning. If the user gets multiple questions wrong simultaneously, this can trigger rate-limits on free LLM tiers.
- **Naive Embeddings**: The repository currently utilizes a mock embedding function for vector calculations. Future iterations will fully integrate an embedding model (like `text-embedding-004`) and a vector database (like ChromaDB) to allow for traversing entire textbooks rather than just truncated strings.

## Local Setup

To run this project locally:

1. Clone the repository.
2. Install the backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Groq API key in your environment variables:
   ```bash
   export GROQ_API_KEY="your-groq-api-key"
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn api.index:app --reload
   ```
5. Serve the static frontend (e.g., using Python's http.server in the `public` directory):
   ```bash
   cd public
   python -m http.server 3000
   ```

## Deployment

This application is configured for seamless deployment on **Vercel**. 
- The `vercel.json` file automatically routes frontend requests to the static `public` directory and backend requests to the serverless `api/index.py` FastAPI instance.
- Ensure `GROQ_API_KEY` is added to your Vercel Environment Variables before deploying.
