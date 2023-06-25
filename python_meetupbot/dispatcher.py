import logging
import sys

import telegram.error
from telegram import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Dispatcher, Filters, MessageHandler, Updater,
                          CallbackQueryHandler, ShippingQueryHandler)

from python_meetup.settings import DEBUG, TELEGRAM_TOKEN
from python_meetupbot.handlers.common import handlers as common_handlers
from python_meetupbot.handlers.meetup import handlers as meetup_handlers
from python_meetupbot.handlers.meetup.static_text import features_choose
from python_meetupbot.handlers.admin.static_text import features_choose

meetup_handlers = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex('^(Гость)$'),
                       meetup_handlers.test),
        MessageHandler(Filters.regex('^(Докладчик)$'),
                       meetup_handlers.test),
        MessageHandler(Filters.regex('^(Организатор)$'),
                       meetup_handlers.organization_option),
        MessageHandler(Filters.regex('^(Выход)$'),
                       meetup_handlers.exit),
    ],
    states={
        meetup_handlers.OPTION: [
            MessageHandler(Filters.text & ~Filters.command, meetup_handlers.choose_admin_button)
        ],
        meetup_handlers.CREATE_MEETUP: [
            MessageHandler(Filters.text & ~Filters.command, meetup_handlers.create_meetup)
        ],
        meetup_handlers.MEETUP_DATE: [
            MessageHandler(Filters.text & ~Filters.command, meetup_handlers.meetup_date)
        ],
        meetup_handlers.MEETUP_START_TIME: [
            MessageHandler(Filters.text & ~Filters.command, meetup_handlers.meetup_start_time)
        ],
        meetup_handlers.MEETUP_END_TIME: [
            MessageHandler(Filters.text & ~Filters.command, meetup_handlers.meetup_end_time)
        ],
    },
    fallbacks=[
        CommandHandler("cancel", common_handlers.command_cancel)
    ]
)


def setup_dispatcher(dp):
    dp.add_handler(meetup_handlers)

    dp.add_handler(CommandHandler("start", common_handlers.command_start))
    dp.add_handler(CommandHandler("cancel", common_handlers.command_cancel))

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f'https://t.me/{bot_info["username"]}'

    print(f"Pooling of '{bot_link}' started")

    updater.start_polling()
    updater.idle()


bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)

n_workers = 1 if DEBUG else 4
dispatcher = setup_dispatcher(
    Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True)
)
