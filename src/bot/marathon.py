from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ChatAction
import logging
import os
from utils.validator import Validator
from db.db import Database, UserInfo

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

database = Database()
database.create_users_table()

TOKEN = os.environ['TOKEN']

AWAITING_NAME_SURNAME, AWAITING_PHONE, AWAITING_EMAIL, \
AWAITING_INTERESTS, AWAITING_ATTEND_REASON, AWAITING_EXPECTATIONS, \
AWAITING_PHYSICAL_STATE, AWAITING_EMOTIONAL_STATE, \
DUMMY, DAILY_RESULTS = range(10)


def start(bot, update):
    update.text.reply_message('Напиши свои Фамилию и Имя.\n\nФормат ввода:\nИванов Иван')
    return AWAITING_NAME_SURNAME


def handle_name(bot, update, user_data):
    if len(update.message.text.split()) < 2:
        update.text.reply_message('Неверный формат ввода, повторите ввод фамилии и имени')
        return AWAITING_NAME_SURNAME

    name, surname = update.message.text.split()
    user_data['name'] = name
    user_data['surname'] = surname
    update.text.reply_message('Напиши свой номер телефона')
    return AWAITING_PHONE


def handle_phone(bot, update, user_data):
    user_data['phone'] = update.text.message
    update.text.reply_message('Напиши адрес своей электронной почты')
    return AWAITING_EMAIL


def handle_email(bot, update, user_data):
    if not Validator.validate_email(update.text.message):
        update.text.reply_message('Неверный формат почты, повторите ввод')

    user_data['email'] = update.text.message
    update.text.reply_message('Какие у тебя интересы (3-5 штук)')
    return AWAITING_INTERESTS


def handle_interests(bot, update, user_data):
    user_data['interests'] = update.text.message
    update.text.reply_message('Почему ты захотел пойти на марафон?')
    return AWAITING_ATTEND_REASON


def handle_attend_reason(bot, update, user_data):
    user_data['attend_reason'] = update.text.message
    update.text.reply_message('Что ты ждешь от недельного марафона?')
    return AWAITING_EXPECTATIONS


def handle_expectations(bot, update, user_data):
    user_data['expectations'] = update.text.message
    update.text.reply_message('Как ты себя чувствуешь сейчас на физическом плане (цифра)')
    return AWAITING_PHYSICAL_STATE


def handle_physical_state(bot, update, user_data):
    if not Validator.validate_digit(update.text.message):
        update.text.reply_message('Неверный формат, введи цифру')
        return AWAITING_PHYSICAL_STATE

    user_data['physical_state'] = update.text.message
    update.text.reply_message('Как ты себя чувствуешь сейчас на эмоциональном плане (цифра)')
    return AWAITING_EMOTIONAL_STATE


def handle_emotional_state(bot, update, user_data):
    if not Validator.validate_digit(update.text.message):
        update.text.reply_message('Неверный формат, введи цифру')
        return AWAITING_EMOTIONAL_STATE

    user_data['emotional_state'] = update.text.message
    database.add_user(UserInfo(user_data['name'], user_data['surname'], user_data['phone'],
                               user_data['email'], user_data['interests'], user_data['attend_reason'],
                               user_data['expectations'], user_data['physical_state'], user_data['emotional_state']))
    update.text.reply_message('Спасибо! Добро пожаловать на марафон!')
    return DUMMY


def handle_dummy(bot, update):
    update.text.reply_message('К сожалению, я не знаю, что на это ответить')
    return DUMMY


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def stop(bot, update):
    update.message.reply_text('До свидания!')
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, request_kwargs={'read_timeout': 10, 'connect_timeout': 10})
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AWAITING_NAME_SURNAME: [MessageHandler(Filters.text, handle_name, pass_user_data=True)],
            AWAITING_PHONE: [MessageHandler(Filters.text, handle_phone, pass_user_data=True)],
            AWAITING_EMAIL: [MessageHandler(Filters.text, handle_email, pass_user_data=True)],
            AWAITING_INTERESTS: [MessageHandler(Filters.text, handle_interests, pass_user_data=True)],
            AWAITING_ATTEND_REASON: [MessageHandler(Filters.text, handle_attend_reason, pass_user_data=True)],
            AWAITING_EXPECTATIONS: [MessageHandler(Filters.text, handle_expectations, pass_user_data=True)],
            AWAITING_PHYSICAL_STATE: [MessageHandler(Filters.text, handle_physical_state, pass_user_data=True)],
            AWAITING_EMOTIONAL_STATE: [MessageHandler(Filters.text, handle_emotional_state, pass_user_data=True)],
            DUMMY: [MessageHandler(Filters.text, handle_dummy)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
