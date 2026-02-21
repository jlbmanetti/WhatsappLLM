"""
WhatsApp + LLM webhook server.

Flow: WhatsApp Cloud API POSTs incoming messages to /webhook → we call OpenAI
→ we POST the reply back to WhatsApp.
"""

import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
from openai import OpenAI

load_dotenv()

# Env (required for webhook and send)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
# Optional: set to your public base URL (e.g. ngrok https URL) to see the full callback URL on startup
APP_PUBLIC_URL = (os.getenv("APP_PUBLIC_URL") or "").rstrip("/")

WHATSAPP_GRAPH_URL = "https://graph.facebook.com/v21.0"

WEBHOOK_PATH = "/webhook"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load env, validate, and print startup info with callback URL for Meta."""
    missing = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not WHATSAPP_TOKEN:
        missing.append("WHATSAPP_TOKEN")
    if not WHATSAPP_PHONE_NUMBER_ID:
        missing.append("WHATSAPP_PHONE_NUMBER_ID")
    if not WEBHOOK_VERIFY_TOKEN:
        missing.append("WEBHOOK_VERIFY_TOKEN")
    if missing:
        print(f"Warning: missing env vars (webhook/send may fail): {missing}")

    # Startup banner: local URL and callback URL for Meta
    print("\n" + "=" * 60)
    print("  WhatsApp LLM – server running")
    print("=" * 60)
    print(f"  Local:        http://localhost:8000")
    print(f"  Webhook path: {WEBHOOK_PATH}")
    if APP_PUBLIC_URL:
        callback_url = f"{APP_PUBLIC_URL}{WEBHOOK_PATH}"
        print(f"  Callback URL for Meta:  {callback_url}")
        print("  → Paste the above into Meta’s Callback URL field.")
    else:
        print("  To see your Callback URL: run ngrok (e.g. ngrok http 8000),")
        print("  then set APP_PUBLIC_URL in .env to the ngrok https URL and restart.")
    print("=" * 60 + "\n")

    yield


app = FastAPI(title="WhatsApp LLM", lifespan=lifespan)


# ----- Webhook: verification (GET) -----


@app.get(WEBHOOK_PATH)
async def webhook_verify(
    mode: str | None = Query(None, alias="hub.mode"),
    token: str | None = Query(None, alias="hub.verify_token"),
    challenge: str | None = Query(None, alias="hub.challenge"),
):
    """Meta calls this to verify the webhook URL. Return hub.challenge as plain text if token matches."""
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN and challenge is not None:
        return PlainTextResponse(content=challenge)
    return PlainTextResponse(content="verification failed", status_code=403)


# ----- Webhook: incoming messages (POST) -----


def get_text_from_body(payload: dict) -> list[tuple[str, str, str]]:
    """
    Parse WhatsApp webhook payload and return list of (user_phone_id, message_id, text).
    Only text messages are returned.
    """
    result = []
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") != "messages":
                    continue
                value = change.get("value", {})
                phone_number_id = value.get("metadata", {}).get("phone_number_id")
                for msg in value.get("messages", []):
                    if msg.get("type") != "text":
                        continue
                    text_block = msg.get("text", {})
                    body = text_block.get("body", "").strip()
                    if not body:
                        continue
                    user_phone = msg.get("from")
                    message_id = msg.get("id", "")
                    result.append((user_phone, message_id, body))
    except Exception:
        pass
    return result


def get_phone_number_id_from_payload(payload: dict) -> str | None:
    """Extract phone_number_id from the first entry (used to send reply)."""
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                pid = value.get("metadata", {}).get("phone_number_id")
                if pid:
                    return pid
    except Exception:
        pass
    return None


def ask_openai(user_message: str) -> str:
    """Send user message to OpenAI and return the assistant reply."""
    if not OPENAI_API_KEY:
        return "Sorry, the assistant is not configured (missing API key)."
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer concisely."},
            {"role": "user", "content": user_message},
        ],
        max_tokens=500,
    )
    choice = response.choices[0]
    return (choice.message.content or "").strip() or "I didn't get a reply."


def send_whatsapp_text(phone_number_id: str, to_phone: str, text: str) -> bool:
    """Send a text message via WhatsApp Cloud API. Returns True on success."""
    url = f"{WHATSAPP_GRAPH_URL}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {"body": text[:4096]},
    }
    try:
        with httpx.Client() as client:
            r = client.post(url, json=body, headers=headers, timeout=30.0)
            return r.status_code == 200
    except Exception:
        return False


@app.post(WEBHOOK_PATH)
async def webhook_receive(request: Request):
    """
    Receive incoming WhatsApp messages from Meta.
    For each text message: call OpenAI, then post reply back to WhatsApp.
    """
    try:
        body = await request.json()
    except Exception:
        return {"status": "bad request"}, 400

    # Meta may send non-message updates (e.g. status); we only handle messages
    if body.get("object") != "whatsapp_business_account":
        return {"status": "ok"}

    phone_number_id = get_phone_number_id_from_payload(body) or WHATSAPP_PHONE_NUMBER_ID
    messages = get_text_from_body(body)

    for user_phone, _message_id, text in messages:
        reply = ask_openai(text)
        send_whatsapp_text(phone_number_id, user_phone, reply)

    return {"status": "ok"}


# ----- Health (optional) -----


@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
