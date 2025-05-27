import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceApi
from dotenv import load_dotenv

# Load environment variables (only needed locally)
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")

# Hugging Face Inference API client
client = InferenceApi(repo_id=HF_MODEL, token=HF_API_KEY)

# Dictionary to store user's selected platform
user_platform_choice = {}

# Generates prompts based on platform
def build_prompt(platform: str, topic: str) -> str:
    if platform == "yt":
        return (
            f"Generate a viral YouTube video content for: '{topic}'.\n"
            f"Include:\n- SEO-friendly title\n- Description with call to action (like, share, subscribe)\n- Relevant hashtags"
        )
    elif platform == "ig":
        return (
            f"Generate an engaging Instagram post for: '{topic}'.\n"
            f"Include:\n- Caption with call to action (like, comment, follow)\n- Viral hashtags"
        )
    return f"Generate content for: {topic}"

# Start command shows platform options
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎥 YouTube", callback_data="yt")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select the platform you want to generate content for:", reply_markup=reply_markup)

# Handles button click
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    platform = query.data
    user_id = query.from_user.id
    user_platform_choice[user_id] = platform
    
    await query.message.reply_text(f"✅ Platform selected: {platform.upper()}\nNow send the topic you want content for.")

# Handles user message (topic)
async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    platform = user_platform_choice.get(user_id)

    if not platform:
        await update.message.reply_text("❗ Please use /start and select a platform first.")
        return

    topic = update.message.text
    prompt = build_prompt(platform, topic)

    await update.message.reply_text("⏳ Generating content, please wait...")

    try:
        # Send prompt to Hugging Face
        response = client(inputs=prompt)
        if isinstance(response, dict) and "generated_text" in response:
            result = response["generated_text"]
        elif isinstance(response, str):
            result = response
        else:
            result = str(response)
        
        await update.message.reply_text(result.strip())
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating content: {e}")

# Main bot launcher
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
