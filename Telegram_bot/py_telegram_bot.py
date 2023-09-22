import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from dotenv import load_dotenv
import os
import sqlite3
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Hello world!')


cursor.execute('SELECT telegram_id FROM chats WHERE username = "client"')
Client_group_id = cursor.fetchone()[0]
cursor.execute('SELECT telegram_id FROM chats WHERE username = "support"')
Support_group_id = cursor.fetchone()[0]
ticket_ids = {}


async def manage_chat_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        user_id = update.effective_user.id
        context.user_data[f'first_message_id_{user_id}'] = update.message.message_id
        keyboard = [[InlineKeyboardButton('Reply', callback_data=f'reply_{chat_id}_{message_id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        cursor.execute('INSERT OR IGNORE INTO tickets (chat_id,client_id,helper_id) VALUES (?,?,?)', (Client_group_id,
                                                                                                      user_id, None))
        conn.commit()

        await context.bot.send_message(chat_id=Support_group_id, text=(f'''{update.effective_user.username} is asking -
    {update.message.text[18:]}'''), reply_markup=reply_markup)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Your message has been sent')

    if 'reply_to' in context.user_data and update.message.reply_to_message:
        chat_id, message_id = context.user_data['reply_to']
        question_id = context.user_data.get('question_id')
        keyboard = [[InlineKeyboardButton('Stop the dialog', callback_data=f'stop_{chat_id}_{message_id}'),
                     InlineKeyboardButton('Additional question', callback_data=f'question_{chat_id}_{message_id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=Client_group_id, text=update.message.text, reply_markup=reply_markup,
                                       reply_to_message_id=question_id)
        del context.user_data['reply_to']
    elif 'additional_question' in context.user_data and context.user_data['additional_question']:
        context.user_data['additional_question'] = False
        keyboard = [[InlineKeyboardButton('Reply', callback_data=f'reply_{chat_id}_{message_id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=Support_group_id, text=(f'''{update.effective_user.username} is asking -
    {update.message.text}'''), reply_markup=reply_markup)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Your message has been sent')


async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id, message_id = query.data.split('_')[1:]
    action = query.data.split('_')[0]

    if action == 'reply':
        context.user_data['reply_to'] = (chat_id, message_id)
        context.user_data['question_id'] = message_id
        await context.bot.send_message(chat_id=Support_group_id,
                                       text=f'{update.effective_user.username} is replying....',
                                       reply_markup=ForceReply())
        await query.edit_message_reply_markup()
    elif action == 'stop':
        await context.bot.send_message(chat_id=Support_group_id, text='The dialog has been stopped. Question closed.')
        await context.bot.send_message(chat_id=Client_group_id, text='The dialog has been stopped. Question closed.')
        await query.edit_message_reply_markup()
    elif action == 'question':
        context.user_data['additional_question'] = True
        await query.edit_message_reply_markup()
        await context.bot.send_message(chat_id=Client_group_id, text='Please enter your additional question:',
                                       reply_markup=ForceReply())


load_dotenv()

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    start_handler = CommandHandler('Start', start)
    application.add_handler(start_handler)
    db_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, manage_chat_interaction)
    application.add_handler(db_handler)
    reply_handler = CallbackQueryHandler(handle_reply_button, pattern='^(reply|stop|question)_')
    application.add_handler(reply_handler)
    application.run_polling()
