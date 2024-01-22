import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from dotenv import load_dotenv
import os
import sqlite3
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='''Hello world!
Bot commands:
/start
/set_support_group_id
/set_client_group_id''')


async def set_support_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    role = cursor.fetchone()[0]

    if role != 'admin':
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Only admins can use this command.')
        return

    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='''Rewrite the command correctly. For example:
/set_support_group_id 123456789''')
        return

    group_id = context.args[0]
    cursor.execute("UPDATE chats SET telegram_id = ? WHERE username = 'support'", (group_id,))
    conn.commit()
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Support group ID updated successfully.')


async def set_client_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    role = cursor.fetchone()[0]

    if role != 'admin':
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Only admins can use this command.')
        return

    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='''Rewrite the command correctly. For example:
/set_client_group_id 123456789''')
        return

    group_id = context.args[0]
    cursor.execute("UPDATE chats SET telegram_id = ? WHERE username = 'client'", (group_id,))
    conn.commit()
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Client group ID updated successfully.')


cursor.execute('SELECT telegram_id FROM chats WHERE username = "support"')
Support_group_id = cursor.fetchone()[0]
cursor.execute('SELECT telegram_id FROM chats WHERE username = "client"')
Client_group_id = cursor.fetchone()[0]
current_ticket_id = None


async def manage_chat_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    global current_ticket_id
    global Client_group_id
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, role) VALUES (?, ?, ?)",
                   (user.id, user.username, 'client'))
    conn.commit()

    chat_id = update.message.chat_id
    message_id = update.message.message_id


    print(chat_id, user.id)
    if chat_id == user.id:
         Client_group_id = chat_id
    print(Client_group_id)

    if update.message.text.startswith('@yasb_testing_bot'):
        user_id = update.effective_user.id
        context.user_data[f'first_message_id_{user_id}'] = update.message.message_id
        keyboard = [[InlineKeyboardButton('Reply', callback_data=f'reply_{chat_id}_{message_id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        cursor.execute('INSERT INTO tickets (chat_id,client_id,helper_id) VALUES (?,?,?)', (Client_group_id, user_id,
                                                                                            None))
        conn.commit()
        ticket_id = cursor.lastrowid
        current_ticket_id = ticket_id

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
    cursor.execute("INSERT INTO messages (ticket_id, text) VALUES (?, ?)", (current_ticket_id, update.message.text))
    conn.commit()


async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_ticket_id
    global Client_group_id

    query = update.callback_query
    await query.answer()
    chat_id, message_id = query.data.split('_')[1:]
    action = query.data.split('_')[0]

    if action == 'reply':
        context.user_data['reply_to'] = (chat_id, message_id)
        context.user_data['question_id'] = message_id
        helper_id = update.effective_user.id
        cursor.execute("UPDATE tickets SET helper_id = ? WHERE chat_id = ?", (helper_id, chat_id))
        conn.commit()
        context.user_data['ticket_id'] = current_ticket_id
        await context.bot.send_message(chat_id=Support_group_id,
                                       text=f'{update.effective_user.username} is replying....',
                                       reply_markup=ForceReply())
        await query.edit_message_reply_markup()
    elif action == 'stop':
        await context.bot.send_message(chat_id=Support_group_id, text='The dialog has been stopped. Question closed.')
        await context.bot.send_message(chat_id=Client_group_id, text='The dialog has been stopped. Question closed.')
        await query.edit_message_reply_markup()
        current_ticket_id = None
        cursor.execute('SELECT telegram_id FROM chats WHERE username = "client"')
        Client_group_id = cursor.fetchone()[0]
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
    application.add_handler(CommandHandler('set_support_group_id', set_support_group_id))
    application.add_handler(CommandHandler('set_client_group_id', set_client_group_id))
    application.run_polling()
