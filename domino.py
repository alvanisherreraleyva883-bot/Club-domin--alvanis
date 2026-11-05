import os
from flask import Flask, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Club Domino Cubano activo!"

@app.route("/app")
def serve_app():
    return send_from_directory(".", "index.html")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎲 JUGAR - ABRIR LOBBY", web_app=WebAppInfo(url=f"{WEBAPP_URL}/app"))]]
    await update.message.reply_text(
        "🇨🇺 *CLUB DE DOMINÓ CUBANO* 🇨🇺\n\n"
        "Bienvenido al Club.\n"
        "Mesas en vivo • Personas reales\n\n"
        "Toca abajo para entrar al Lobby.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

def main():
    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start))
    import threading
    threading.Thread(target=lambda: tg_app.run_polling(), daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
