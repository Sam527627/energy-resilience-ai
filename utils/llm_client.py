import anthropic
import json
from config.settings import ANTHROPIC_API_KEY


def get_client():
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def query_agent(system_prompt: str, user_message: str, max_tokens: int = 1500) -> str:
    """Call Claude with a system + user message. Returns text response."""
    client = get_client()
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    except Exception as e:
        return f"[Agent error: {str(e)}]"


def query_agent_json(system_prompt: str, user_message: str, max_tokens: int = 2000) -> dict:
    """Call Claude expecting a JSON response. Returns parsed dict."""
    system_with_json = system_prompt + "\n\nCRITICAL: Respond ONLY with valid JSON. No markdown, no backticks, no preamble."
    client = get_client()
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=system_with_json,
            messages=[{"role": "user", "content": user_message}]
        )
        text = response.content[0].text.strip()
        # Strip any accidental markdown
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}
