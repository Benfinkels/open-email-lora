from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI(title="Email LoRA Oracle")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "alfred-v1"

class EmailRequest(BaseModel):
    sender: str
    subject: str
    body: str

@app.post("/classify")
async def classify_email(request: EmailRequest):
    """
    Classifies an email using the custom-tuned LoRA model.
    This is non-invasive and does not modify the original email.
    """
    prompt = f"Sender: {request.sender}\nSubject: {request.subject}\nBody: {request.body}\n\nClassify this email:"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        prediction = response.json().get("response", "ERROR")
        
        # Return a standardized JSON response that other workflows can parse
        return {
            "prediction": prediction.strip(),
            "confidence": 1.0, # Placeholder for future logic
            "model": MODEL_NAME
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)
