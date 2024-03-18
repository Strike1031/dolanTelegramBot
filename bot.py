# start
import sys

import os
from dotenv import load_dotenv
import requests
import httpx
# end

load_dotenv()

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update)

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import platform
import asyncio

# States
START_STATE, END_STATE = range(2)

TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
DOLAN_TRANSLATE_API_KEY = os.environ.get('DOLAN_TRANSLATE_API_KEY')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send message on `/start`."""

    # Get user that sent /start and log his name
    user = update.effective_user
    return START_STATE

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    return ConversationHandler.END

async def get_dolan_response(text):
    # The URL to which the request is sent
    url = 'https://api.funtranslations.com/translate/dolan.json'
    # Headers to be sent with the request
    headers = {
        'X-Funtranslations-Api-Secret': DOLAN_TRANSLATE_API_KEY,
    }
    # Data to be sent in the request body
    data = {
        'text': {text}
    }
    # Sending a POST request
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
    # Checking if the request was successful
    if response.status_code == 200:
        # The request was successful; printing the response text
        response_json = response.json()
        translated_text = response_json['contents']['translated']
        return translated_text[2:-2]
    else:
        # The request failed; printing the status code and response text
        print(f"Failed: status code: {response.status_code}")
        print(response.text)
        return "translation failed"

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Handle all messages from customers """
    # Get the message from the update
    message = update.message.text
    user = update.effective_user
    # Print messages to the console
    if message.startswith("/t"):
        message = message[3:]
        response = await get_dolan_response(message)
        response = response.replace('\\n', ' ')
        await update.message.reply_html(response)

def main():
    """Run the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT, message_handler)
        ],
        states={
            START_STATE: [
            ],
            END_STATE: [
                CallbackQueryHandler(end),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
