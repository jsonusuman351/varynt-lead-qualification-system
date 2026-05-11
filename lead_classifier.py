import openai
import json
import time

client = openai.OpenAI(api_key="your-api-key-here")

CLASSIFICATION_PROMPT = """
You are a B2B lead qualification expert for VARYNT, an AI-powered business platform.

Given this lead's information, classify them as Hot, Warm, or Cold.

Lead Info:
Name: {name}
Company: {company}
Message: {message}
Budget: {budget}
Timeline: {timeline}

Definitions:
- HOT: Strong buying intent, specific need, mentions budget or urgency, decision-maker
- WARM: Some interest, vague requirements, exploring options, no clear timeline
- COLD: Generic inquiry, no clear business need, possibly spam or just browsing

Rules:
- Be strict with Hot — only if clear buying signals exist
- Default to Warm if ambiguous
- Respond in JSON only

Output format:
{{"classification": "Hot/Warm/Cold", "confidence": 0.0, "reason": "one line"}}
"""

def classify_lead(lead_data: dict) -> dict:
    """
    Classifies a lead using LLM with rule-based fallback.
    Returns: dict with classification, confidence, reason
    """
    # Step 1: Input validation
    if not lead_data.get("message") or len(lead_data["message"].strip()) < 10:
        return {
            "classification": "Cold",
            "confidence": 1.0,
            "reason": "Insufficient input provided"
        }

    prompt = CLASSIFICATION_PROMPT.format(
        name=lead_data.get("name", "N/A"),
        company=lead_data.get("company", "N/A"),
        message=lead_data.get("message", "N/A"),
        budget=lead_data.get("budget", "Not mentioned"),
        timeline=lead_data.get("timeline", "Not mentioned")
    )

    # Step 2: LLM call with retry
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=150,
                timeout=10
            )
            raw = response.choices[0].message.content.strip()
            result = json.loads(raw)

            # Step 3: Low confidence → flag for human review
            if result.get("confidence", 1.0) < 0.6:
                result["needs_review"] = True
            else:
                result["needs_review"] = False

            return result

        except json.JSONDecodeError:
            # LLM returned non-JSON, try again
            time.sleep(1)
            continue
        except Exception as e:
            print(f"LLM attempt {attempt+1} failed: {e}")
            time.sleep(1)
            continue

    # Step 4: Rule-based fallback if LLM fails
    print("Falling back to rule-based classifier")
    return rule_based_fallback(lead_data)


def rule_based_fallback(lead_data: dict) -> dict:
    """
    Simple keyword-based fallback when LLM is unavailable.
    """
    message = lead_data.get("message", "").lower()
    budget = lead_data.get("budget", "").lower()

    hot_signals = ["urgent", "asap", "immediately", "budget approved",
                   "ready to start", "need this now", "decision made"]
    cold_signals = ["just browsing", "no budget", "not sure yet",
                    "maybe later", "just curious", "testing"]

    if any(k in message or k in budget for k in hot_signals):
        return {"classification": "Hot", "confidence": 0.7,
                "reason": "Keyword match – hot signal", "needs_review": False}
    elif any(k in message for k in cold_signals):
        return {"classification": "Cold", "confidence": 0.7,
                "reason": "Keyword match – cold signal", "needs_review": False}
    else:
        return {"classification": "Warm", "confidence": 0.5,
                "reason": "No clear signal – defaulted to Warm", "needs_review": True}


# Quick test
if __name__ == "__main__":
    test_lead = {
        "name": "Rahul Sharma",
        "company": "TechCorp India",
        "message": "We need your platform urgently. Budget is approved, 
                    looking to onboard next week.",
        "budget": "50000 INR",
        "timeline": "1 week"
    }
    result = classify_lead(test_lead)
    print(json.dumps(result, indent=2))
