import logging
from telegram import Update
from dotenv import load_dotenv
import os
import sqlite3
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import Message_texts

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        status TEXT
    )
''')
conn.commit()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username
    status = 'not available'
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, status) VALUES (?, ?, ?)",
                   (user_id, username, status))
    conn.commit()


    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=Message_texts.GREETING)
async def WhoIam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Retrieve user information from the SQLite database
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()

    if user_info:
        id, user_id, username, status = user_info
        user_info_text = (f"User ID: {user_id}\n"
                          f"Username: @{username}\n"
                          f"status: {status}\n")

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=user_info_text)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="User information not found.")
load_dotenv()

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    users_handler = CommandHandler('WhoIam', WhoIam)
    application.add_handler(users_handler)

    application.run_polling()