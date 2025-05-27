import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from huggingface_hub import InferenceApi
from dotenv import load_dotenv

# Load environment variables (if running locally)
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")

# Hugging Face client
client = InferenceApi(repo_id=HF_MODEL, token=HF_API_KEY)

# Store user context (in memory)
user_topics = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Send me a topic to generate SEO content for YouTube or Instagram.")

# Message handler (receives topic)
async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text
    user_id = update.effective_user.id
    user_topics[user_id] = topic

    keyboard = [
        [InlineKeyboardButton("📺 YouTube", callback_data="yt")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig")],
        [InlineKeyboardButton("📱 Both", callback_data="both")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Choose a platform to generate content:", reply_markup=reply_markup)

# Callback handler for button press
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    platform = query.data
    user_id = query.from_user.id

    topic = user_topics.get(user_id)
    if not topic:
        await query.edit_message_text("❗ Topic not found. Please send a topic first.")
        return

    prompt = build_prompt(platform, topic)

    await query.edit_message_text("⏳ Generating content...")

    try:
        response = client(inputs=prompt, raw_response=True)
        generated_text = response.text.strip()
        await context.bot.send_message(chat_id=query.message.chat_id, text=generated_text)
    except Exception as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"❌ Error: {e}")

# Prompt generator
def build_prompt(platform: str, topic: str) -> str:
    if platform == "yt":
        return f"""Generate an SEO-optimized YouTube video:
- Title
- Description with Like, Share & Subscribe call-to-actions
- Viral hashtags

Topic: {topic}"""
    elif platform == "ig":
        return f"""Generate an Instagram caption:
- Engaging title
- Caption with Like, Comment, Follow CTA
- Viral hashtags

Topic: {topic}"""
    else:
        return f"""Generate content for both YouTube and Instagram for the topic: {topic}.
Include:
1. YouTube Title, Description, Hashtags
2. Instagram Caption, Hashtags
Be engaging and SEO-friendly."""

# Main function
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
