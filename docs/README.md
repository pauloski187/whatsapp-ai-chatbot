# AI Support Chatbot Developer Setup

## 1. Clone and enter project

```bash
git clone <your-repo-url>
cd whatsapp-ai-chatbot/backend
```

## 2. Create virtual environment and install dependencies

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure environment variables

```bash
cp .env.example .env
```

Fill all values in `.env`:
- Groq key and model
- Twilio credentials and WhatsApp sender
- Meta webhook credentials and Instagram account ID
- Google Sheet ID and service account JSON path
- Business name/tone and Chroma collection name

## 4. Run the API

```bash
uvicorn main:app --reload
```

Default local URL: `http://127.0.0.1:8000`

## 5. Ingest a knowledge file (RAG)

Use the sample test file:

```bash
curl -X POST "http://127.0.0.1:8000/ingest" \
  -F "file=@../tests/sample_business.txt"
```

Expected response contains `chunks_stored`.

## 6. Test chat endpoint

```bash
curl -X POST "http://127.0.0.1:8000/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user_1","message":"What time do you open?"}'
```

## 7. Local WhatsApp testing with Twilio + ngrok

1. Start API locally:
```bash
uvicorn main:app --reload
```
2. Expose local server:
```bash
ngrok http 8000
```
3. Copy HTTPS forwarding URL from ngrok, for example `https://abc123.ngrok-free.app`.
4. In Twilio console, set WhatsApp webhook URL to:
`https://abc123.ngrok-free.app/webhook/whatsapp`
5. Send a WhatsApp message to your Twilio sandbox/number and confirm bot replies.

## 8. Website widget integration

Host `widget/widget.js` and `widget/widget.css` publicly, then add:

```html
<script src="https://your-domain/widget.js" data-api-url="https://your-backend-url"></script>
```
