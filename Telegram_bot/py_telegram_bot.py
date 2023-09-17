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
    await context.bot.send_message(chat_id=update.effective_chat.id, text=Message_texts.GREETING)
load_dotenv()

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()