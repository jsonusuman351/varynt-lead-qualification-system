

# VARYNT – AI Lead Qualification + Smart Response System

## Overview
An async, production-ready AI pipeline that classifies incoming leads as Hot/Warm/Cold and generates personalized responses using LLMs.

## Architecture
Form/Chat Input → Validation → Redis Queue → LLM Classifier
→ Response Generator → CRM Update → PostgreSQL
↓ (on failure)
Rule-based Fallback → Human Review Queue

## Project Structure
varynt-lead-qualification-system/
├── README.md
├── lead_classifier.py       # Core classification logic
├── response_generator.py    # Personalized response generation
├── app.py                   # FastAPI endpoints
├── requirements.txt         # Dependencies
└── config.py                # Config and constants

## Tech Stack
- Python 3.11
- FastAPI
- OpenAI GPT-4o
- Redis (queue)
- PostgreSQL
- Prometheus + Grafana (monitoring)

## Setup
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

## Key Design Decisions
- Async queue so user never waits
- LLM fallback to rule-based on failure
- Low temperature (0.2) to prevent hallucination
- Confidence threshold < 0.6 → human review
