import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")

# Initialize Hugging Face client
client = InferenceClient(model=HF_MODEL, token=HF_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 Hello! I am your AI content bot.\n\n"
        "Use /generate <your prompt> to get AI-generated text for YouTube or Instagram.\n\n"
        "Example:\n/generate Write a YouTube title and description about AI."
    )
    await update.message.reply_text(welcome_text)

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("⚠️ Please provide a prompt after /generate command.")
        return
    
    await update.message.reply_text("⏳ Generating content, please wait...")

    try:
        # Call Hugging Face API text generation endpoint
        response = client.text_generation(prompt=prompt, max_new_tokens=150)
        generated_text = response[0]["generated_text"]

        # Reply with generated text
        await update.message.reply_text(generated_text)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating content: {e}")

def main():
    # Build Telegram bot application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))

    print("Bot started. Waiting for commands...")
    app.run_polling()

if __name__ == "__main__":
    main()
