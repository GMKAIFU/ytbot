import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from huggingface_hub import InferenceApi
from dotenv import load_dotenv

# Load env variables locally (not needed on Railway)
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")

# Initialize Hugging Face InferenceApi client
client = InferenceApi(repo_id=HF_MODEL, token=HF_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 Hi! I generate SEO-friendly content for YouTube and Instagram.\n\n"
        "Use /generate <platform> <topic> to get optimized content.\n"
        "Platforms:\n"
        "  yt - YouTube\n"
        "  ig - Instagram\n\n"
        "Example:\n"
        "/generate yt How to learn Python programming\n"
        "/generate ig Best summer outfits 2025\n"
    )
    await update.message.reply_text(welcome_text)

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
    else:
        return (
            f"Generate SEO-friendly YouTube and Instagram content for the topic: '{topic}'.\n"
            f"Include:\n"
            f"1) YouTube Title\n2) YouTube Description with calls to action\n3) YouTube hashtags\n"
            f"4) Instagram Caption with calls to action\n5) Instagram hashtags\n"
            f"Format your answer clearly with headings."
        )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please provide platform and topic after /generate command.")
        return
    
    platform = context.args[0].lower()
    topic = " ".join(context.args[1:])

    if platform not in ["yt", "ig"]:
        # Assume full content generation for both if platform not specified
        topic = " ".join(context.args)
        platform = "both"
    
    if not topic:
        await update.message.reply_text("⚠️ Please provide a topic after the platform.")
        return
    
    await update.message.reply_text("⏳ Generating content, please wait...")

    prompt = build_prompt(platform, topic)

    try:
        response = client(inputs=prompt, max_new_tokens=300)
        # HuggingFace returns a list of dict with "generated_text"
        generated_text = response[0]["generated_text"]
        await update.message.reply_text(generated_text)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating content: {e}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))

    print("Bot started. Waiting for commands...")
    app.run_polling()

if __name__ == "__main__":
    main()

