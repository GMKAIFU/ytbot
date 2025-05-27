import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceApi
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")

client = InferenceApi(repo_id=HF_MODEL, token=HF_API_KEY)

# Store user platform choice
user_platform_choice = {}

def build_prompt(platform: str, topic: str) -> str:
    if platform == "yt":
        return (
            f"Generate an SEO-friendly YouTube video title, description with calls to action "
            f"(like, share, subscribe), and relevant viral hashtags for the topic: '{topic}'. "
            f"Format the response as:\n"
            f"Title: <title>\nDescription: <description>\nHashtags: <hashtags>"
        )
    elif platform == "ig":
        return (
            f"Generate an Instagram post caption with an engaging title, description, calls to action "
            f"(like, comment, follow), and relevant viral hashtags for the topic: '{topic}'. "
            f"Format the response as:\n"
            f"Title: <title>\nCaption: <caption>\nHashtags: <hashtags>"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("YouTube", callback_data="yt")],
        [InlineKeyboardButton("Instagram", callback_data="ig")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a platform to generate content:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    platform = query.data
    user_id = query.from_user.id
    user_platform_choice[user_id] = platform

    await query.message.reply_text(f"You selected: {platform.upper()}. Now send your topic...")

async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    topic = update.message.text

    platform = user_platform_choice.get(user_id)

    if not platform:
        await update.message.reply_text("⚠️ Please use /start and select a platform first.")
        return

    await update.message.reply_text("⏳ Generating content, please wait...")

    try:
        prompt = build_prompt(platform, topic)
        response = client(inputs=prompt, raw_response=True)
        await update.message.reply_text(response.text.strip())
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating content: {e}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic))

    print("Bot started. Waiting for users...")
    app.run_polling()

if __name__ == "__main__":
    main()
