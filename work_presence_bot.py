#!/usr/bin/env python

# work_presence_bot.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import user_handlers as handlers


# function to handle errors occurred in the dispatcher
def error(update, context):
    update.message.reply_text('An error occurred')


def main():
    token = ""

    with open('token.txt') as file_token:
        token = file_token.readline()

    # create the updater, that will automatically create also a dispatcher and a queue to 
    # make them dialogue
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", handlers.start))
    dispatcher.add_handler(CommandHandler("stats", handlers.stats))
    dispatcher.add_handler(CommandHandler("menu", handlers.menu))
    dispatcher.add_handler(CommandHandler("help", handlers.help))
    dispatcher.add_handler(CallbackQueryHandler(handlers.button))

    # add an handler for errors
    dispatcher.add_error_handler(error)

    # start bot
    updater.start_polling()

    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
