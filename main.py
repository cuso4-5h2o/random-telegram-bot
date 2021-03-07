import logging
import os
import json
import uuid
import string
import random

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    Update,
    ParseMode
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    CallbackContext
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger_file_handler = logging.FileHandler('./log/info.log')
logger_file_handler.setLevel(logging.INFO)
logger_file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(logger_file_handler)


def log_with_user(user, content) -> None:
    log_text = f"User {user.full_name} (Username: {user.username}, ID: {user.id}) {content}"
    logger.info(log_text)


def command_start(update, context) -> None:
    chat = update.effective_chat
    user = update.effective_user
    text = """<b>Commands of This Bot:</b>
/random: Generate some random text.
<b>Links:</b>
<a href="https://github.com/cuso4-5h2o/simple-random-bot">Source code</a>, <a href="https://pi3k-akt.lofter.com/post/1f0804ed_1c7a995f7">Avatar source</a>"""
    context.bot.send_message(chat_id=chat.id,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             disable_web_page_preview=True)
    log_with_user(user, "started this bot.")


def command_random(update, context) -> None:
    chat = update.effective_chat
    user = update.effective_user
    text = """Ok, tell me which kind of random text you need?
<i>Hint: In order to prevent the physical address from leaking, <code>8000000000</code> will be used as the node number in UUID v1 mode, and only one can be generated at a time in that mode as well.</i>"""
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("UUID v1", callback_data="random:1:u1"),
            InlineKeyboardButton("UUID v4", callback_data="random:1:u4")
        ],
        [
            InlineKeyboardButton("6 digits", callback_data="random:1:6d"),
            InlineKeyboardButton("12 digits", callback_data="random:1:12d"),
            InlineKeyboardButton("16 digits", callback_data="random:1:16d")
        ],
        [
            InlineKeyboardButton("6 hex digits", callback_data="random:1:6hd"),
            InlineKeyboardButton(
                "12 hex digits", callback_data="random:1:12hd")
        ],
        [
            InlineKeyboardButton("8 digits or letters (a-z)",
                                 callback_data="random:1:8daz")
        ],
        [
            InlineKeyboardButton("16 digits or letters (A-z)",
                                 callback_data="random:1:16dAz")
        ]
    ])
    context.bot.send_message(chat_id=chat.id,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             reply_markup=reply_markup)
    log_with_user(user, "tried to get random text.")


def callback_query(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    query = update.callback_query
    query.answer()
    random_data = "\n"
    query_data = query.data.split(":")
    if query_data[0] == "random":
        log_with_user(user, f"got {query_data[1]} random {query_data[2]}.")
        for index in range(int(query_data[1])):
            if query_data[2] == "u1":
                random_item = uuid.uuid1(node=8000000000)
            if query_data[2] == "u4":
                random_item = uuid.uuid4()
            if query_data[2] == "6d":
                random_item = ""
                for _ in range(6):
                    random_item += random.choice(string.digits)
            if query_data[2] == "12d":
                random_item = ""
                for _ in range(12):
                    random_item += random.choice(string.digits)
            if query_data[2] == "16d":
                random_item = ""
                for _ in range(16):
                    random_item += random.choice(string.digits)
            if query_data[2] == "6hd":
                random_item = ""
                for _ in range(6):
                    random_item += random.choice(string.digits +
                                                 string.hexdigits)
                random_item = random_item.lower()
            if query_data[2] == "12hd":
                random_item = ""
                for _ in range(12):
                    random_item += random.choice(string.digits +
                                                 string.hexdigits)
                random_item = random_item.lower()
            if query_data[2] == "8daz":
                random_item = ""
                for _ in range(8):
                    random_item += random.choice(string.digits +
                                                 string.ascii_lowercase)
            if query_data[2] == "16dAz":
                random_item = ""
                for _ in range(16):
                    random_item += random.choice(string.digits +
                                                 string.ascii_letters)
            random_data += f"<b>({str(query_data[2])}) {str(index)}: </b><code>{random_item}</code>\n"
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Another 1", callback_data="random:1:"+query_data[2]),
                InlineKeyboardButton(
                    "Another 5", callback_data="random:5:"+query_data[2])
            ],
            [
                InlineKeyboardButton(
                    "Another 10", callback_data="random:10:"+query_data[2]),
                InlineKeyboardButton(
                    "Another 20", callback_data="random:20:"+query_data[2])
            ],
            [
                InlineKeyboardButton(
                    "Another 50", callback_data="random:50:"+query_data[2])
            ]
        ]) if not query_data[2] == "u1" else InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Another 1", callback_data="random:1:"+query_data[2]),
            ]
        ])
        query.edit_message_text(text=random_data.strip(),
                                parse_mode=ParseMode.HTML,
                                reply_markup=reply_markup)


if __name__ == "__main__":
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", command_start))
    dispatcher.add_handler(CommandHandler("random", command_random))
    dispatcher.add_handler(CallbackQueryHandler(callback_query))
    updater.start_polling()
    updater.idle()
