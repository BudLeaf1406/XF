# -*- coding: utf-8 -*-
import logging
import traceback

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Dispatcher, MessageHandler, CallbackQueryHandler, CommandHandler, ConversationHandler, \
    Filters
import config
import manager_options
from config import strings

conv = ConversationHandler(
    entry_points=[CommandHandler(callback=manager_options.start_command, command="start", pass_user_data=True)],
    states={
        "MANAGER_MENU": [CallbackQueryHandler(callback=manager_options.manager_menu,
                                              pattern="^{}$|^{}$|^{}$|^{}$|^{}$|^{}$|^{}$".format(strings.ADD_LINE,
                                                                                        strings.REMOVE_LINE,
                                                                                        strings.CHANGE_TEXT,
                                                                                        strings.CHANNEL_POST,
                                                                                        strings.CHANGE_CHANNEL,
                                                                                        strings.CREATE_CHANNEL,
                                                                                        strings.DELETE_CHANNEL
                                                                                        ),
                                              pass_user_data=True)],
        "ADD_BUTTON_TEXT": [MessageHandler(filters=Filters.text,
                                           callback=manager_options.add_button_text,
                                           pass_user_data=True)],
        "ADD_BUTTON_LINK": [MessageHandler(filters=Filters.text,
                                           callback=manager_options.add_button_link,
                                           pass_user_data=True)],
        "REMOVE_BUTTON_LINK": [MessageHandler(filters=Filters.text,
                                              callback=manager_options.remove_button_link,
                                              pass_user_data=True)],
        "ADDED_BUTTON": [CallbackQueryHandler(callback=manager_options.add_another_button,
                                              pattern="^{}$|^{}$".format(
                                                  strings.ANOTHER_BUTTON_NO,
                                                  strings.ANOTHER_BUTTON_YES),
                                              pass_user_data=True)],
        "NEW_TEXT": [MessageHandler(filters=Filters.text,
                                    callback=manager_options.new_text,
                                    pass_user_data=True)],
        "ADD_CHANNEL_TEXT": [MessageHandler(filters=Filters.text,
                                            callback=manager_options.add_channel_text,
                                            pass_user_data=True)],
        "DELETE_CHANNEL_TEXT": [MessageHandler(filters=Filters.text,
                                               callback=manager_options.delete_channel_text,
                                               pass_user_data=True)]
    },
    fallbacks=[
        CallbackQueryHandler(callback=manager_options.start_command, pattern="^{}$".format(strings.GO_TO_START),
                             pass_user_data=True)],
    allow_reentry=True, name="manager_handler", persistent=True)
