import os
import requests

from fastapi import  FastAPI, Request
from google import genai

TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
RENDER_URL=os.getenv("RENDER_URL")


TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
app = FastAPI()

genclient = genai.Client(api_key=GEMINI_API_KEY)


@app.get("/")
def default():
    return {"status": "Bot is running"}

@app.get("/webhook")
async def webhook(request: Request):
    data = await request.json()

    msg = data.get("message")
    if msg is None:
        return {"ok": True}

    chat_id = msg["chat"]["id"]

    user_text = msg.get("text")
    if user_text is None:
        return {"ok": True}

    if user_text == "/start":
        send_msg(chat_id, "Привіт , це локальний АІ")
        return {"ok": True}
    try:
        ai_answer = send_q_to_ai(user_text)
        send_msg(chat_id, ai_answer)
    except Exception as e:
        send_msg(chat_id,f"Спробуй ще раз, error: {e}")


def send_q_to_ai(text:str)->str:
    rep = genclient.models.generate_content(model="gemini-3-flash-preview",contents=text)
    if hasattr(rep, "text") and rep.text:
        return rep.text
    return "Щось пішло не так"
def send_msg(chat_id:int , text:str):
    requests.post(
    f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },timeout= 30)
 