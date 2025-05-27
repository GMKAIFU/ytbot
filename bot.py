import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from huggingface_hub import InferenceApi
from dotenv import load_dotenv

# Load environment variables (for local)
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "openai-community/gpt2")  # default: GPT-2

# Initialize Hugging Face client
client = InferenceApi(repo_id=HF_MODEL, token=HF_API_KEY)

# Store topics per user
user_topics = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send a topic. I’ll generate YouTube or Instagram content for it.")

async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text
    user_id = update.effective_user.id
    user_topics[user_id] = topic

    buttons = [
        [InlineKeyboardButton("📺 YouTube", callback_data="yt")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig")],
        [InlineKeyboardButton("📱 Both", callback_data="both")]
    ]
    await update.message.reply_text("Choose a platform:", reply_markup=InlineKeyboardMarkup(buttons))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    platform = query.data
    user_id = query.from_user.id

    topic = user_topics.get(user_id)
    if not topic:
        await query.edit_message_text("❗ Please send a topic first.")
        return

    prompt = build_prompt(platform, topic)
    await query
