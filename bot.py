#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot that excutes commands sent through Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage: Meant for AWS EC2 machines 
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging, requests, time, subprocess

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
bot_token = 'TOKEN'
bot_chatID = 'CHATID'
def ping(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=HTML&text=' + str(bot_message)
    response = requests.get(send_text)
    return response.json()
def ec2():
    try:
        r=requests.get("http://169.254.169.254/latest/meta-data/public-ipv4")
        out= "<b>"+ str(r.text) + "</b>\n"
        r=requests.get("http://169.254.169.254/latest/dynamic/instance-identity/document")
        r=r.json()
    except Exception as e:
        out = str(e.__class__.__name__)+": Failed to retrive EC2 Metadata."
        return out
    for key, value in r.items():
        out = out + str(key) + ":" + str(value) + "\n"
    return out
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')
    ping(ec2())


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Just type in the commands, and it will get executed and output will be returned here :)",parse_mode='HTML')


def runCommand(update, context):
    """Run commands"""
    if str(update.message.chat_id)!=bot_chatID:
        update.message.reply_text("<b>Sorry you're not authorized</b>", parse_mode='HTML')
        return
    try:
        s = str(update.message.text)
        s = s.split()
        #out = subprocess.check_output(s,stderr=subprocess.STDOUT)
        out = subprocess.Popen(s, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:
        ping(str(e))
        return
    o = out.stdout.read()
    ping(str(o.decode("utf-8")))
    #update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    ping("Instance started at "+time.asctime( time.localtime(time.time()) ))
    ping(ec2())
    updater = Updater(bot_token, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on command 
    dp.add_handler(MessageHandler(Filters.text, runCommand))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
