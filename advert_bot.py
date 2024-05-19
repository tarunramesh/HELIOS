from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import tempfile
from detect_advert import detect, clear
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()
# Get the bot token and username from environment variables
TOKEN: Final = os.getenv("TOKEN")
USR_NAME: Final = os.getenv("USR_NAME")

# Handler for the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I can find billboards in your image.")

# Handler for the /clear command
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear()
    await update.message.reply_text("Cleared all the backed up images from the server.")

# Handler for the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send an image to me so I can process it for you.")

# Function to handle responses to text messages
def handle_response(text: str) -> str:
    return "/help -> What I can do."

# Handler for text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == "group":
        if USR_NAME in text:
            # Remove the bot's username from the text and handle the response
            new_text: str = text.replace(USR_NAME, '').strip()  
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot: ', response)
    await update.message.reply_text(response)

# Handler for image messages
async def handle_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    image_file = await context.bot.get_file(file_id)
    temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=".jpg")
    with os.fdopen(temp_file_fd, 'wb') as temp_file:
        await image_file.download_to_memory(temp_file)
    # Process the image and get the path of the processed image
    processed_image_path, _ = detect(temp_file_path)
    with open(processed_image_path, 'rb') as photo:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
    # Remove the temporary file
    os.remove(temp_file_path)

# Handler for errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == "__main__":
    print("Starting Bot...")
    # Initialize the bot application
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('clear', clear_command))
    app.add_handler(CommandHandler('help', help_command))

    # Add message handlers
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_images))

    # Add error handler
    app.add_error_handler(error)

    print("Polling...")
    # Start polling for updates
    app.run_polling(poll_interval=3)
