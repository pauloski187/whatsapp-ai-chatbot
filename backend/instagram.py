"""Instagram webhook routes for Meta Graph API integration."""

import asyncio

import requests
from fastapi import APIRouter, HTTPException, Query, Request

from chat import chat_service
from config import settings


router = APIRouter(prefix="/webhook/instagram", tags=["instagram"])


def _send_instagram_message(recipient_id: str, text: str) -> None:
    """Send a direct reply message through Meta Graph API."""
    url = f"https://graph.facebook.com/v20.0/{settings.INSTAGRAM_ACCOUNT_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.META_PAGE_ACCESS_TOKEN}"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
    }
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    if response.status_code >= 400:
        raise RuntimeError(f"Meta API error {response.status_code}: {response.text}")


@router.get("")
async def verify_instagram_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> str:
    """Verify Meta webhook setup by validating the shared token."""
    try:
        if hub_mode == "subscribe" and hub_verify_token == settings.META_VERIFY_TOKEN:
            return hub_challenge
        raise HTTPException(status_code=403, detail="Webhook verification failed.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Instagram verification error: {exc}") from exc


@router.post("")
async def receive_instagram_message(request: Request) -> dict:
    """Receive Instagram webhook events, generate an AI reply, and send response."""
    try:
        payload = await request.json()
        messaging = payload["entry"][0]["messaging"][0]
        sender_id = messaging["sender"]["id"]
        message_text = messaging["message"]["text"].strip()

        reply_text = await asyncio.to_thread(chat_service.get_reply, sender_id, message_text, "instagram")
        await asyncio.to_thread(_send_instagram_message, sender_id, reply_text)
        return {"status": "ok"}
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Instagram payload: missing {exc}") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Instagram webhook error: {exc}") from exc
