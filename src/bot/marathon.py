from telegram.ext import Updater, CallbackContext, MessageHandler, CommandHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ChatAction, Update
import logging
import os
from dotenv import load_dotenv
from utils.validator import Validator
from db.db import Database, UserInfo

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

database = Database()
database.create_users_table()

TOKEN = os.getenv('TOKEN')

AWAITING_NAME_SURNAME, AWAITING_PHONE, AWAITING_EMAIL, \
AWAITING_INTERESTS, AWAITING_ATTEND_REASON, AWAITING_EXPECTATIONS, \
AWAITING_PHYSICAL_STATE, AWAITING_EMOTIONAL_STATE, \
DUMMY, DAILY_RESULTS = range(10)

INTERESTS = database.get_interests_list()


def get_interests_keyboard():
    keyboard = []
    interests_row = []
    for interest in INTERESTS:
        interests_row.append(interest)
        if len(interests_row) == 3:
            keyboard.append(interests_row)
            interests_row = []
    if interests_row:
        keyboard.append(interests_row)

    return keyboard


INTERESTS_KEYBOARD = get_interests_keyboard()


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Напиши свои Фамилию и Имя.\n\nФормат ввода:\nИванов Иван')
    return AWAITING_NAME_SURNAME


def handle_name(update: Update, context: CallbackContext):
    if len(update.message.text.split()) != 2:
        update.message.reply_text('Неверный формат ввода, повторите ввод фамилии и имени')
        return AWAITING_NAME_SURNAME

    name, surname = update.message.text.split()
    context.user_data['name'] = name
    context.user_data['surname'] = surname
    update.message.reply_text('Напиши свой номер телефона')
    return AWAITING_PHONE


def handle_phone(update: Update, context: CallbackContext):
    context.user_data['phone'] = update.message.text
    update.message.reply_text('Напиши адрес своей электронной почты')
    return AWAITING_EMAIL


def handle_email(update: Update, context: CallbackContext):
    if not Validator.validate_email(update.message.text):
        update.message.reply_text('Неверный формат почты, повторите ввод')
        return AWAITING_EMAIL

    context.user_data['email'] = update.message.text
    update.message.reply_text('Давай выберем твои интересы! Выбери любую область из списка',
                              reply_markup=ReplyKeyboardMarkup(INTERESTS_KEYBOARD))
    return AWAITING_INTERESTS


def handle_interests(update: Update, context: CallbackContext):
    user_interests = context.user_data.setdefault('interests', [])
    if update.message.text not in INTERESTS:
        update.message.reply_text('Давай выбирать интересы только из списка',
                                  reply_markup=ReplyKeyboardMarkup(INTERESTS_KEYBOARD, one_time_keyboard=True))
        return AWAITING_INTERESTS
    user_interests.append(update.message.text)
    if len(user_interests) == 1:
        update.message.reply_text('Что еще тебя интересует?', reply_markup=ReplyKeyboardMarkup(INTERESTS_KEYBOARD))
        return AWAITING_INTERESTS
    elif len(user_interests) == 2:
        update.message.reply_text('Давай выберем последний интерес',
                                  reply_markup=ReplyKeyboardMarkup(INTERESTS_KEYBOARD, one_time_keyboard=True))
        return AWAITING_INTERESTS

    update.message.reply_text('Отлично! Почему ты захотел пойти на марафон?')
    return AWAITING_ATTEND_REASON


def handle_attend_reason(update: Update, context: CallbackContext):
    context.user_data['attend_reason'] = update.message.text
    update.message.reply_text('Что ты ждешь от недельного марафона?')
    return AWAITING_EXPECTATIONS


def handle_expectations(update: Update, context: CallbackContext):
    context.user_data['expectations'] = update.message.text
    update.message.reply_text('Как ты себя чувствуешь сейчас на физическом плане (цифра)')
    return AWAITING_PHYSICAL_STATE


def handle_physical_state(update: Update, context: CallbackContext):
    if not Validator.validate_digit(update.message.text):
        update.message.reply_text('Неверный формат, введи цифру')
        return AWAITING_PHYSICAL_STATE

    context.user_data['physical_state'] = update.message.text
    update.message.reply_text('Как ты себя чувствуешь сейчас на эмоциональном плане (цифра)')
    return AWAITING_EMOTIONAL_STATE


def handle_emotional_state(update: Update, context: CallbackContext):
    if not Validator.validate_digit(update.message.text):
        update.message.reply_text('Неверный формат, введи цифру')
        return AWAITING_EMOTIONAL_STATE

    context.user_data['emotional_state'] = update.message.text
    database.add_user(UserInfo(context.user_data['name'], context.user_data['surname'], context.user_data['phone'],
                               context.user_data['email'], context.user_data['interests'],
                               context.user_data['attend_reason'],
                               context.user_data['expectations'], context.user_data['physical_state'],
                               context.user_data['emotional_state']))
    update.message.reply_text('Спасибо! Добро пожаловать на марафон!')
    return DUMMY


def handle_dummy(update: Update, context: CallbackContext):
    update.message.reply_text('К сожалению, я не знаю, что на это ответить')
    return DUMMY


def error(update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def stop(update):
    update.message.reply_text('До свидания!')
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, request_kwargs={'read_timeout': 10, 'connect_timeout': 10})
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AWAITING_NAME_SURNAME: [MessageHandler(Filters.text, handle_name)],
            AWAITING_PHONE: [MessageHandler(Filters.text, handle_phone)],
            AWAITING_EMAIL: [MessageHandler(Filters.text, handle_email)],
            AWAITING_INTERESTS: [MessageHandler(Filters.text, handle_interests)],
            AWAITING_ATTEND_REASON: [MessageHandler(Filters.text, handle_attend_reason)],
            AWAITING_EXPECTATIONS: [MessageHandler(Filters.text, handle_expectations)],
            AWAITING_PHYSICAL_STATE: [MessageHandler(Filters.text, handle_physical_state)],
            AWAITING_EMOTIONAL_STATE: [MessageHandler(Filters.text, handle_emotional_state)],
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
