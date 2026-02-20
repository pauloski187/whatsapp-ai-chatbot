"""Twilio WhatsApp webhook routes."""

import asyncio

from fastapi import APIRouter, Form, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from chat import chat_service
from config import settings


router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])


def _get_twilio_client() -> Client:
    """Create a Twilio REST client from configured credentials."""
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


@router.get("")
async def verify_whatsapp_webhook() -> dict:
    """Provide a basic verification response for webhook health checks."""
    try:
        return {"status": "ok", "message": "WhatsApp webhook is active."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verification failed: {exc}") from exc


@router.post("")
async def receive_whatsapp_message(From: str = Form(...), Body: str = Form(...)) -> Response:
    """Receive WhatsApp webhook payload, generate reply, and return TwiML."""
    try:
        user_id = From
        user_message = Body.strip()
        reply_text = await asyncio.to_thread(chat_service.get_reply, user_id, user_message, "whatsapp")

        twilio_from = settings.TWILIO_WHATSAPP_NUMBER
        twilio_to = From
        print(f"Twilio WhatsApp send from_: {twilio_from}")
        print(f"Twilio WhatsApp send to: {twilio_to}")

        twiml = MessagingResponse()
        twiml.message(reply_text)

        try:
            twilio_client = _get_twilio_client()
            await asyncio.to_thread(
                twilio_client.messages.create,
                from_=twilio_from,
                to=twilio_to,
                body=reply_text,
            )
        except Exception as send_exc:
            print(f"Twilio send failed: {send_exc}")

        return Response(content=str(twiml), media_type="application/xml")
    except Exception as exc:
        print(f"WhatsApp webhook error: {exc}")
        fallback = MessagingResponse()
        fallback.message("Sorry, something went wrong. Please try again shortly.")
        return Response(content=str(fallback), media_type="application/xml")
