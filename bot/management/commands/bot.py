from django.core.management.base import BaseCommand
from telegram.utils.request import Request
from telegram import Bot
from django.conf import settings
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters, \
    CallbackQueryHandler

from bot.views import *


class Command(BaseCommand):
    help = 'Telegram-bot'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=None,
            read_timeout=None
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
        )

        updater = Updater(
            bot=bot,
            use_context=True
        )
        conv_hand = ConversationHandler(
            entry_points=[
                MessageHandler(Filters.text, start)
            ],
            states={
                state_user_name: [
                    MessageHandler(Filters.text, command_user_name)
                ],
                state_user_contact: [
                    MessageHandler(Filters.contact, command_user_contact)
                ],
                state_user_main: [
                    MessageHandler(Filters.regex('^(' + addorder + ')$'), command_user_addorder),
                    MessageHandler(Filters.regex('^(' + savatcha + ')$'), command_user_savatcha),
                    MessageHandler(Filters.regex('^(' + orderhistory + ')$'), command_user_orderhistory),
                    MessageHandler(Filters.regex('^(' + hisobkitob + ')$'), command_hisobkitob),
                    MessageHandler(Filters.regex('^(' + info + ')$'), command_info),
                    CallbackQueryHandler(command_user_product)
                ],
                state_user_savatcha: [
                    CallbackQueryHandler(command_user_savatcha_conf)
                ],
                state_user_muddat:[
                    CallbackQueryHandler(command_user_muddat)
                ]
            },
            fallbacks=[
                CommandHandler('start', start)
            ]

        )
        updater.dispatcher.add_handler(conv_hand)

        updater.start_polling()
        updater.idle()
