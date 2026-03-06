import os
import requests
from datetime import datetime
import sys

from fastapi import  FastAPI, Request
from google import genai
from dotenv import load_dotenv

load_dotenv()

def log_message(message: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_text = f"{timestamp} - {message}"
    print(log_text, file=sys.stdout)
    try:
        with open('bot.txt', 'a', encoding='utf-8') as f:
            f.write(log_text + "\n")
    except Exception as e:
        print(f"Could not write to file: {e}")

TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
RENDER_URL=os.getenv("RENDER_URL")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
app = FastAPI()

genclient = genai.Client(api_key=GEMINI_API_KEY)


@app.get("/")
def default():
    log_message("Default endpoint called - Bot is running")
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    log_message(f"Webhook request received: {data}")

    msg = data.get("message")
    if msg is None:
        log_message("No message in webhook data")
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    log_message(f"Message from chat_id: {chat_id}")

    user_text = msg.get("text")
    if user_text is None:
        log_message(f"No text in message from chat_id: {chat_id}")
        return {"ok": True}

    log_message(f"User message: {user_text}")
    
    if user_text == "/start":
        log_message(f"Start command received from chat_id: {chat_id}")
        send_msg(chat_id, "Привіт , це локальний АІ")
        return {"ok": True}
    try:
        ai_answer = send_q_to_ai(user_text)
        send_msg(chat_id, ai_answer)
    except Exception as e:
        log_message(f"Error processing message: {e}")
        send_msg(chat_id,f"Спробуй ще раз, error: {e}")


def send_q_to_ai(text:str)->str:
    log_message(f"Sending query to AI: {text}")
    rep = genclient.models.generate_content(model="gemini-3-flash-preview",contents=text)
    if hasattr(rep, "text") and rep.text:
        log_message(f"AI response: {rep.text}")
        return rep.text
    log_message("AI response is empty or has no text attribute")
    return "Щось пішло не так"

def send_msg(chat_id:int , text:str):
    log_message(f"Sending message to chat_id {chat_id}: {text}")
    try:
        requests.post(
        f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },timeout= 30)
        log_message(f"Message successfully sent to chat_id {chat_id}")
    except Exception as e:
        log_message(f"Failed to send message to chat_id {chat_id}: {e}")
 