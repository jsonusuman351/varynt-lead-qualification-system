import openai
import json

client = openai.OpenAI(api_key="your-api-key-here")

RESPONSE_PROMPT = """
You are a professional sales assistant for VARYNT, an AI-powered business platform.

A new lead has been classified as: {classification}

Lead Details:
- Name: {name}
- Company: {company}
- Their Message: {message}
- Budget: {budget}

Instructions:
- Write a SHORT, personalized email reply (3-4 sentences only)
- Reference something SPECIFIC from their message (not generic)
- Tone: Urgent/direct for Hot, Helpful/informative for Warm, Light/exploratory for Cold
- Do NOT use: "Thank you for your interest", "Hope this finds you well"
- Do NOT mention features or pricing not confirmed above
- End with ONE clear call to action

Return only the email body, no subject line needed.
"""

def generate_response(lead_data: dict, classification: str) -> str:
    """
    Generates a personalized response based on lead data and classification.
    """
    prompt = RESPONSE_PROMPT.format(
        classification=classification,
        name=lead_data.get("name", "there"),
        company=lead_data.get("company", "your company"),
        message=lead_data.get("message", ""),
        budget=lead_data.get("budget", "not specified")
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=200,
            timeout=10
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Response generation failed: {e}")
        return get_fallback_response(classification, lead_data.get("name", "there"))


def get_fallback_response(classification: str, name: str) -> str:
    """Static fallback responses by tier."""
    templates = {
        "Hot": f"Hi {name}, we've reviewed your request and want to move fast. "
               f"Can we schedule a 15-minute call today to get things rolling?",
        "Warm": f"Hi {name}, great to hear from you! "
                f"I'd love to understand your needs better — "
                f"would a quick call this week work for you?",
        "Cold": f"Hi {name}, thanks for reaching out to VARYNT. "
                f"Feel free to explore our platform and reach back "
                f"when you're ready to discuss further."
    }
    return templates.get(classification, templates["Warm"])
