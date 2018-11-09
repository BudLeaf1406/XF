# -*- coding: utf-8 -*-
import logging
import traceback

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, Dispatcher, MessageHandler, CallbackQueryHandler, CommandHandler, PicklePersistence)
import config
from config import strings
import pickle
import manager_handler
def main():
    pp = PicklePersistence(filename="mybot")
    updater = Updater(config.TOKEN, persistence=pp)

    dp = updater.dispatcher
    dp.add_handler(manager_handler.conv)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)
    tb = traceback.format_exc()
    logger.warning(tb)


# Add logging to file to be able to debug more easily
# Add signal handler to change logging level / Reload config.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
if __name__ == "__main__":
    main()