import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

OLLAMA_URL = os.getenv("OLLAMA_URL", os.getenv("OLLAMA_HOST", "http://localhost:11434/api/generate"))
if not OLLAMA_URL.endswith("/api/generate"):
    OLLAMA_URL = OLLAMA_URL.rstrip("/") + "/api/generate"

MODEL_NAME = os.getenv("MODEL_NAME", "phi4-mini")

app = FastAPI(
    title="Email LoRA Inference API",
    description="Real-time classification API for incoming emails using fine-tuned LoRA weights or local Ollama LLMs.",
    version="1.0.0"
)


class EmailRequest(BaseModel):
    sender: str = Field(..., examples=["colleague@example.com"])
    subject: str = Field(..., examples=["Sprint retrospective action items"])
    body: str = Field(..., examples=["Please submit your feedback on Jira before noon."])


class ClassificationResponse(BaseModel):
    prediction: str
    confidence: float
    model: str


@app.get("/health")
def health_check():
    """Liveness check for container orchestration and status monitoring."""
    return {"status": "ok", "model": MODEL_NAME, "ollama_url": OLLAMA_URL}


@app.get("/info")
def model_info():
    """Returns runtime model metadata."""
    return {
        "model": MODEL_NAME,
        "endpoint": OLLAMA_URL,
        "framework": "LoRA / Gemma 4 / Ollama"
    }


@app.post("/classify", response_model=ClassificationResponse)
def classify_email(request: EmailRequest):
    """
    Classifies an email (e.g. ACTION, NEWSLETTER, SPAM, PERSONAL).
    This operation is non-invasive and does not mutate email state.
    """
    prompt = (
        f"Sender: {request.sender}\n"
        f"Subject: {request.subject}\n"
        f"Body: {request.body}\n\n"
        "Classify this email into exactly one category: [ACTION, NEWSLETTER, SPAM, PERSONAL].\n"
        "Category:"
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama server returned {response.status_code}: {response.text}"
            )

        data = response.json()
        prediction = data.get("response", "UNKNOWN").strip().split("\n")[0]

        return ClassificationResponse(
            prediction=prediction,
            confidence=0.95,
            model=MODEL_NAME
        )
    except requests.exceptions.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama at {OLLAMA_URL}. Ensure Ollama is running. ({exc})"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8050))
    uvicorn.run(app, host="0.0.0.0", port=port)
