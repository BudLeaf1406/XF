# -*- coding: utf-8 -*-
import logging
import traceback

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Dispatcher, MessageHandler, CallbackQueryHandler, CommandHandler, ConversationHandler
import config
from config import strings
import pickle


def show_keyboard(user_data):
    for line in user_data[strings.KEYBOARD]:
        for b in line:
            print(b)


def start_command(bot,update,user_data):
    if hasattr(update, 'from_user'):
        from_user = update.from_user
    else:
        from_user = update.message.from_user

    print(user_data[strings.CHANNEL_LIST])
    if from_user.id in config.ADMINS:
        if strings.CHANNEL_INDEX not in user_data:
            user_data[strings.CHANNEL_INDEX] = 0

        load_settings(user_data)

        print(user_data)

        keyboard = [[InlineKeyboardButton(text="הוספת שורה",callback_data=strings.ADD_LINE),
                    InlineKeyboardButton(text="הסרת כפתור",callback_data=strings.REMOVE_LINE)],
                    [InlineKeyboardButton(text="שינוי טקסט",callback_data=strings.CHANGE_TEXT),
                    InlineKeyboardButton(text="שלח לערוץ", callback_data=strings.CHANNEL_POST)],
                    [InlineKeyboardButton(text="ערוץ נוכחי: {}".format(user_data[strings.CHANNEL_LIST][user_data[strings.CHANNEL_INDEX]]), callback_data=strings.CHANGE_CHANNEL)],
                    [InlineKeyboardButton(text="יצירת ערוץ",callback_data=strings.CREATE_CHANNEL),
                     InlineKeyboardButton(text="מחיקת ערוץ",callback_data=strings.DELETE_CHANNEL)]]
        update.message.reply_text(text="תפריט ניהול",reply_markup=InlineKeyboardMarkup(keyboard))

        return "MANAGER_MENU"
    else:
        return ConversationHandler.END


def manager_menu(bot,update,user_data):
    user_data["row"] = None
    data = update.callback_query.data
    update = update.callback_query
    print(data)
    if strings.ADD_LINE in data:
        update.message.reply_text("אנא שלח את הטקסט לכפתור")
        return "ADD_BUTTON_TEXT"
    elif strings.REMOVE_LINE in data:
        update.message.reply_text("אנא שלח את הלינק של הכפתור")
        return "REMOVE_BUTTON_LINK"
    elif strings.CHANGE_TEXT in data:
        update.message.reply_text("אנא שלח את הטקסט החדש")
        return "NEW_TEXT"
    elif strings.CHANNEL_POST in data:
        load_settings(user_data)

        show_keyboard(user_data)
        bot.send_message(chat_id=user_data[strings.CHANNEL_LIST][user_data[strings.CHANNEL_INDEX]],text=user_data[strings.MESSAGE_TEXT], reply_markup=InlineKeyboardMarkup(user_data[strings.KEYBOARD]))
        update.message.reply_text("נשלחה מודעה בערוץ")
        return start_command(bot,update,user_data)
    elif strings.CHANGE_CHANNEL in data:
        print(len(user_data[strings.CHANNEL_LIST]))
        print(user_data[strings.CHANNEL_INDEX])
        if user_data[strings.CHANNEL_INDEX] == len(user_data[strings.CHANNEL_LIST]) -1:
            user_data[strings.CHANNEL_INDEX] = 0
        else:
            user_data[strings.CHANNEL_INDEX] += 1
        update.message.reply_text("הערוץ שונה ל:{}".format(user_data[strings.CHANNEL_LIST][int(user_data[strings.CHANNEL_INDEX])]))
        load_settings(user_data)

        return start_command(bot,update,user_data)
    elif strings.CREATE_CHANNEL in data:

        update.message.reply_text("אנא שלח את היוזר של הערוץ")
        return "ADD_CHANNEL_TEXT"
    elif strings.DELETE_CHANNEL in data:
        update.message.reply_text("אנא שלח את היוזר של הערוץ")
        return "DELETE_CHANNEL_TEXT"


def add_button_text(bot,update,user_data):
    txt = update.message.text

    button = InlineKeyboardButton(text="", url="")
    button.text = txt
    user_data["button"] = button

    update.message.reply_text(text="אנא שלח את הלינק של הכפתור")
    return "ADD_BUTTON_LINK"


def add_button_link(bot,update,user_data):
    txt= update.message.text
    row = []
    if user_data["row"] is None:
        user_data["row"] = row
    else:
        row = user_data["row"]

    button = user_data["button"]
    button.url = txt
    user_data["button"] = button

    row.append(button)
    user_data["row"] = row
    keyboard = [[InlineKeyboardButton(text="כן",callback_data=strings.ANOTHER_BUTTON_YES),InlineKeyboardButton(text="לא",callback_data=strings.ANOTHER_BUTTON_NO)]]
    update.message.reply_text(text="האם אתה רוצה להוסיף עוד כפתור לשורה?",reply_markup=InlineKeyboardMarkup(keyboard))
    return "ADDED_BUTTON"


def remove_button_link(bot,update,user_data):
    txt = update.message.text
    found_button = False
    load_settings(user_data)
    for line in user_data[strings.KEYBOARD]:
        for button in line:
            if button.url == txt:
                line.remove(button)
                found_button = True

    save_settings(user_data)
    if found_button:
        update.message.reply_text("הכפתור נמחק")
    else:
        update.message.reply_text("לא נמצא כפתור עם כתובת זו")
    return start_command(bot,update,user_data)


def add_another_button(bot,update,user_data):
    data = update.callback_query.data
    update = update.callback_query
    if strings.ANOTHER_BUTTON_YES in data:
        update.message.reply_text("אנא שלח את הטקסט לכפתור")
        return "ADD_BUTTON_TEXT"
    elif strings.ANOTHER_BUTTON_NO in data:
        row = user_data["row"]

        user_data[strings.KEYBOARD].append(row)

        user_data["row"] = None
        user_data["button"] = None
        update.message.reply_text("השורה נוספה")

        save_settings(user_data)
        return start_command(bot,update,user_data)


def add_channel_text(bot,update,user_data):
    txt = update.message.text

    if txt == "":
        update.message.reply_text('אנא כתוב יוזר של ערוץ')
        return start_command(bot,update,user_data)
    if "@" not in txt:
        txt = "@" + txt
    if strings.CHANNEL_LIST not in user_data:
        user_data[strings.CHANNEL_LIST] = config.CHANNEL_LIST

    user_data[strings.CHANNEL_LIST].append(txt)

    update.message.reply_text("הערוץ נוסף")
    return start_command(bot,update,user_data)


def delete_channel_text(bot,update,user_data):
    txt = update.message.text

    if txt == "":
        update.message.reply_text('אנא כתוב יוזר של ערוץ')
        return start_command(bot, update, user_data)
    if "@" not in txt:
        txt = "@" + txt

    user_data[strings.CHANNEL_LIST].remove(txt)

    user_data[strings.CHANNEL_LIST] = user_data[strings.CHANNEL_LIST]
    update.message.reply_text("הערוץ נמחק")
    return start_command(bot,update,user_data)


def new_text(bot,update,user_data):
    txt = update.message.text
    user_data[strings.MESSAGE_TEXT] = txt
    save_settings(user_data)
    update.message.reply_text("הטקסט שונה")
    return start_command(bot,update,user_data)


def edit_keyboard(bot,update,user_data):
    keyboard = user_data[strings.KEYBOARD]
    index = 0
    for line in keyboard:
        line.append(InlineKeyboardButton(text="מחק", callback_data=strings.DELETE_ROW + "|" + str(index)))
        line.append(InlineKeyboardButton(text="ערוך",callback_data=strings.EDIT_ROW + "|" + str(index)))
        index += 1

    keyboard.append([[InlineKeyboardButton(text="הוסף שורה",callback_data=strings.ADD_LINE)]])

    update.message.edit_message(text="עריכת מקלדת",reply_markup =InlineKeyboardMarkup(keyboard))
    return "EDIT_KEYBOARD_SELECT"


def edit_keyboard_select(bot,update,user_data):
    data = update.callback_query.data
    update = update.callback_query

    if strings.EDIT_ROW in data:
        update.message.edit_text(text="בחר כפתור לערוך",reply_markup=InlineKeyboardMarkup([user_data[strings.KEYBOARD][int(data.split('|')[1])]]))
        return "EDIT_BUTTON"
    elif strings.DELETE_ROW in data:
        del user_data[strings.KEYBOARD][int(data.split('|')[1])]


def load_settings(user_data):
    try:
        settings = user_data[config.CHANNEL_LIST[user_data[strings.CHANNEL_INDEX]]]

        user_data[strings.KEYBOARD] = settings[0]
        user_data[strings.MESSAGE_TEXT] = settings[1]
    except KeyError:
        user_data[strings.CHANNEL_LIST][int(user_data[strings.CHANNEL_INDEX])] = []
        user_data[strings.KEYBOARD] = []
        user_data[strings.MESSAGE_TEXT] = "ללא טקסט"
    except IndexError:
        print(user_data[strings.CHANNEL_INDEX])
        user_data[strings.CHANNEL_LIST][int(user_data[strings.CHANNEL_INDEX])] = []
        user_data[strings.KEYBOARD] = []
        user_data[strings.MESSAGE_TEXT] = "ללא טקסט"


def save_settings(user_data):
    user_data[user_data[strings.CHANNEL_LIST][user_data[strings.CHANNEL_INDEX]]] = [user_data[strings.KEYBOARD],user_data[strings.MESSAGE_TEXT]]


