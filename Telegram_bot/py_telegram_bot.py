import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
import re
import os
import sqlite3
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler,MessageHandler, filters
import Message_texts

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=Message_texts.GREETING)


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username
    role = 'client'

    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, role) VALUES (?, ?, ?)",
                   (user_id, username, role))
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()

    if user_info:
        id, user_id, username, role = user_info
        user_info_text = (f"User ID: {user_id}\n"
                          f"Username: @{username}\n"
                          f"Role: {role}\n")

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=user_info_text)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="User information not found.")


async def save_message_to_db_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username
    role = 'client'

    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, role) VALUES (?, ?, ?)",
                   (user_id, username, role))
    conn.commit()

    chat_id = update.message.chat_id
    message_id = update.message.message_id
    if update.message.text.startswith('@yasb_testing_bot'):
        await context.bot.forward_message(chat_id=-4050412601, from_chat_id=chat_id, message_id=message_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Your message has been sent')
    else:
        pass


load_dotenv()

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    start_handler = CommandHandler('Start', start)
    application.add_handler(start_handler)
    users_handler = CommandHandler('WhoamI', whoami)
    application.add_handler(users_handler)
    db_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, save_message_to_db_client)
    application.add_handler(db_handler)

    application.run_polling()
