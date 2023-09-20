import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup,ForceReply
from dotenv import load_dotenv
import os
import sqlite3
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler,MessageHandler, filters,CallbackQueryHandler
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


Client_id = '-4063636151'
Support_id = '-4050412601'

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
    if 'reply_to' in context.user_data and update.message.reply_to_message:
        chat_id, message_id = context.user_data['reply_to']
        await context.bot.send_message(chat_id=Client_id, text=update.message.text)
        del context.user_data['reply_to']
    elif update.message.text.startswith('@yasb_testing_bot'):
        keyboard = [[InlineKeyboardButton('Reply', callback_data=f'reply_{chat_id}_{message_id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        forwarded_message = await context.bot.send_message(chat_id=-4050412601,
                                                           text=(f'''{update.effective_user.username} is answering -
{update.message.text}'''), reply_markup=reply_markup)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Your message has been sent')
    else:
        pass


async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id, message_id = query.data.split('_')[1:]
    context.user_data['reply_to'] = (chat_id, message_id)
    await context.bot.send_message(chat_id=Support_id, text=f'{update.effective_user.username} is replying....',
                                   reply_markup=ForceReply())


load_dotenv()


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    start_handler = CommandHandler('Start', start)
    application.add_handler(start_handler)
    db_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, save_message_to_db_client)
    application.add_handler(db_handler)
    reply_handler = CallbackQueryHandler(handle_reply_button, pattern='^reply_')
    application.add_handler(reply_handler)
    application.run_polling()