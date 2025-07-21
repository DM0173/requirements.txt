from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes
import openai
import requests
import os

# Конфигурация
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID_DAY = "N8lIVPsFkvOoqev5Csxo"
VOICE_ID_NIGHT = "Atp5cNFg1Wj5gyKD7HWV"

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# AI-ответ и озвучка
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_text}],
    )

    ai_text = response["choices"][0]["message"]["content"]

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": ai_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
    }

    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID_DAY}", headers=headers, json=data)
    
    if r.status_code == 200:
        update.message.chat.send_audio(audio=r.content)
    else:
        await update.message.reply_text(ai_text)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я Адель. Напиши мне что-нибудь 💬")

# Инициализация Telegram-бота
def run_bot():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

# Запуск
if __name__ == "__main__":
    run_bot()
