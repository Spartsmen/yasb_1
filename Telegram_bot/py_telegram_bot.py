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

cursor.execute('SELECT telegram_id FROM chats WHERE username = "client"')
Client_group_id = cursor.fetchone()[0]
cursor.execute('SELECT telegram_id FROM chats WHERE username = "support"')
Support_group_id = cursor.fetchone()[0]


async def save_message_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        first_message_id = context.user_data.get(f'first_message_id_{user_id}')
        await context.bot.send_message(chat_id=Client_group_id, text=update.message.text,reply_to_message_id=first_message_id)
        del context.user_data['reply_to']
    elif update.message.text.startswith('@yasb_testing_bot'):
        user_id = update.effective_user.id
        context.user_data[f'first_message_id_{user_id}'] = update.message.message_id
        keyboard = [[InlineKeyboardButton('Reply', callback_data=f'reply_{chat_id}_{message_id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        forwarded_message = await context.bot.send_message(chat_id=Support_group_id,
                                                           text=(f'''{update.effective_user.username} is asking -
{update.message.text[19:]}'''), reply_markup=reply_markup)

        await context.bot.send_message(chat_id=update.effective_chat.id, text='Your message has been sent')
    ticket_number = context.user_data.get('ticket_number')
    message_text = update.message.text
    cursor.execute("INSERT INTO messages (ticket_id, text) VALUES (?, ?)",
                       (ticket_number, message_text))
    conn.commit()


async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id, message_id = query.data.split('_')[1:]
    context.user_data['reply_to'] = (chat_id, message_id)
    await context.bot.send_message(chat_id=Support_group_id, text=f'{update.effective_user.username} is replying....',
                                   reply_markup=ForceReply())
    await query.edit_message_reply_markup()
    client_id = update.effective_user.id
    supporter_id = query.from_user.id
    cursor.execute("INSERT OR IGNORE INTO tickets (chat_id,client_id, helper_id) VALUES (?, ?, ?)",
                   (Client_group_id, client_id, supporter_id))
    conn.commit()
    cursor.execute(f'SELECT id FROM tickets WHERE client_id ={client_id}')
    context.user_data['ticket_number'] = cursor.fetchone()[0]


load_dotenv()


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    start_handler = CommandHandler('Start', start)
    application.add_handler(start_handler)
    db_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, save_message_to_db)
    application.add_handler(db_handler)
    reply_handler = CallbackQueryHandler(handle_reply_button, pattern='^reply_')
    application.add_handler(reply_handler)
    application.run_polling()