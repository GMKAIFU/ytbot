import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from huggingface_hub import InferenceClient

# Load from Railway environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "openai-community/gpt2")

# Initialize HF client
client = InferenceClient(model=HF_MODEL, token=HF_API_KEY)

# Store user selection in-memory (not persistent)
user_choices = {}

# Start command with platform selection
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("YouTube", callback_data="yt")],
        [InlineKeyboardButton("Instagram", callback_data="ig")]
    ]
    await update.message.reply_text("📱 Choose a platform to generate content for:", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback when user presses a button
async def handle_platform_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    platform = query.data
    user_choices[user_id] = platform
    await query.edit_message_text(f"✅ Platform selected: {platform.upper()}\n\nNow send me a topic!")

# User sends a topic
async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    platform = user_choices.get(user_id)

    if not platform:
        await update.message.reply_text("⚠️ Please select a platform first using /start.")
        return

    topic = update.message.text
    prompt = build_prompt(platform, topic)

    await update.message.reply_text("⏳ Generating content...")

    try:
        output = client.text_generation(prompt, max_new_tokens=250)
        await update.message.reply_text(output)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating content:\n{e}")

# Prompt builder
def build_prompt(platform: str, topic: str) -> str:
    if platform == "yt":
        return (
            f"Generate a YouTube video title, SEO-friendly description with CTA, and trending hashtags for:\n{topic}\n"
            f"Format: Title: ..., Description: ..., Hashtags: ..."
        )
    elif platform == "ig":
        return (
            f"Generate an Instagram caption with a catchy title, engaging text, CTA, and trending hashtags for:\n{topic}\n"
            f"Format: Title: ..., Caption: ..., Hashtags: ..."
        )
    return f"Generate SEO content for: {topic}"

# Run bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_platform_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
