from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from lead_classifier import classify_lead
from response_generator import generate_response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VARYNT Lead Qualification API", version="1.0.0")

class LeadInput(BaseModel):
    name: str
    company: str
    message: str
    budget: str = ""
    timeline: str = ""
    email: str = ""

    @validator("message")
    def message_not_empty(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError("Message too short or empty")
        return v

    @validator("name")
    def name_not_empty(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Name required")
        return v

@app.post("/qualify-lead")
async def qualify_lead(lead: LeadInput):
    try:
        logger.info(f"Processing lead: {lead.name} from {lead.company}")

        # Step 1: Classify
        classification_result = classify_lead(lead.dict())
        classification = classification_result["classification"]

        # Step 2: Generate response
        response_text = generate_response(lead.dict(), classification)

        # Step 3: Return result
        return {
            "status": "success",
            "lead_name": lead.name,
            "classification": classification,
            "confidence": classification_result.get("confidence"),
            "needs_human_review": classification_result.get("needs_review", False),
            "generated_response": response_text,
            "reason": classification_result.get("reason")
        }

    except Exception as e:
        logger.error(f"Pipeline failed for {lead.name}: {e}")
        raise HTTPException(status_code=500, detail="Processing failed, lead queued for review")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "VARYNT Lead Qualification"}
