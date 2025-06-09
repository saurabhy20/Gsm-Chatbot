import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Auto-reply message configuration
AUTO_REPLY_TEXT = "Thanks for your message! I'll get back to you soon."
ADMIN_USER_ID = 6009143798  # Replace with your actual Telegram user ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=None
    )

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send auto-reply to any non-command message."""
    message = update.message
    
    # Don't reply to admins
    if message.from_user.id == ADMIN_USER_ID:
        return
        
    # Check if message is from a group chat
    if message.chat.type != "private":
        # Reply in group chats only if bot is mentioned
        if message.text and context.bot.username in message.text:
            await message.reply_text(AUTO_REPLY_TEXT)
    else:
        # Always reply in private chats
        await message.reply_text(AUTO_REPLY_TEXT)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and send notification to admin."""
    logger.error(msg="Exception while handling update:", exc_info=context.error)
    
    # Only send error notifications from non-group chats
    if update.effective_chat.type == "private":
        text = (
            "⚠️ An error occurred!\n\n"
            f"Error: {context.error}\n"
            f"Update: {update}"
        )
        await context.bot.send_message(chat_id=ADMIN_USER_ID, text=text)

def main():
    """Start the bot."""
    # Create Application
    application = Application.builder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    # Message handler for auto-replies
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        auto_reply
    ))

    # Error handler
    application.add_error_handler(error_handler)

    # Start polling
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
