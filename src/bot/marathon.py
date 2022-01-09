import datetime

import pytz
from telegram.ext import Updater, CallbackContext, MessageHandler, CommandHandler, Filters, \
    ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, Update
import logging
import os
from dotenv import load_dotenv
from utils.validator import Validator
from utils.interests import get_interests_list
from storage.sheets import SheetsManager, UserInfo

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sheets = SheetsManager()
sheets.create_users_table()

TOKEN = os.getenv('TOKEN')

AWAITING_NAME_SURNAME, AWAITING_PHONE, AWAITING_EMAIL, \
AWAITING_INTERESTS, AWAITING_ATTEND_REASON, AWAITING_EXPECTATIONS, \
AWAITING_PHYSICAL_STATE, AWAITING_EMOTIONAL_STATE, \
DUMMY, AWAITING_TASK_DONE, AWAITING_TASK_FEAR, AWAITING_LINK = range(12)

INTERESTS = get_interests_list()
YES_NO_KEYBOARD = ReplyKeyboardMarkup([['Да', 'Нет']], resize_keyboard=True,
                                      one_time_keyboard=True)


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


def get_tasks_keyboard():
    return ReplyKeyboardMarkup([[task] for task in sheets.get_today_tasks()], resize_keyboard=True,
                               one_time_keyboard=True)


INTERESTS_KEYBOARD = get_interests_keyboard()


def start(update: Update, context: CallbackContext):
    context.user_data['signed_up'] = True  # TODO: change to False
    context.job_queue.run_daily(morning_reminder, days=(0, 1, 2, 3, 4, 5, 6),
                                time=datetime.time(hour=11, minute=0, tzinfo=pytz.timezone('Europe/Moscow')),
                                context=(update.message.chat_id, context.user_data),
                                name=f'{str(update.message.chat_id)}-morning')
    context.job_queue.run_daily(daily_results, days=(0, 1, 2, 3, 4, 5, 6),
                                time=datetime.time(hour=10, minute=26, tzinfo=pytz.timezone('Europe/Moscow')),
                                context=(update.message.chat_id, context.user_data),
                                name=f'{str(update.message.chat_id)}-evening')

    update.message.reply_text('Напиши свои Фамилию и Имя.\n\nФормат ввода:\nИванов Иван')
    return AWAITING_NAME_SURNAME
    #return DUMMY


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
                              reply_markup=ReplyKeyboardMarkup(INTERESTS_KEYBOARD, one_time_keyboard=True))
    return AWAITING_INTERESTS


def handle_interests(update: Update, context: CallbackContext):
    user_interests = context.user_data.setdefault('interests', [])
    if update.message.text not in INTERESTS:
        update.message.reply_text('Давай выбирать интересы только из списка',
                                  reply_markup=ReplyKeyboardMarkup(INTERESTS_KEYBOARD, one_time_keyboard=True))
        return AWAITING_INTERESTS
    user_interests.append(update.message.text)
    if len(user_interests) == 1:
        update.message.reply_text('Что еще тебя интересует?',
                                  reply_markup=ReplyKeyboardMarkup(INTERESTS_KEYBOARD, one_time_keyboard=True))
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
    update.message.reply_text('Как ты себя чувствуешь сейчас на физическом плане? (цифра)')
    return AWAITING_PHYSICAL_STATE


def handle_physical_state(update: Update, context: CallbackContext):
    if not Validator.validate_digit(update.message.text):
        update.message.reply_text('Неверный формат, введи цифру')
        return AWAITING_PHYSICAL_STATE

    context.user_data['physical_state'] = update.message.text
    update.message.reply_text('Как ты себя чувствуешь сейчас на эмоциональном плане? (цифра)')
    return AWAITING_EMOTIONAL_STATE


def handle_emotional_state(update: Update, context: CallbackContext):
    if not Validator.validate_digit(update.message.text):
        update.message.reply_text('Неверный формат, введи цифру')
        return AWAITING_EMOTIONAL_STATE

    if context.user_data.get('awaiting_daily_results', False):
        update.message.reply_text('Насколько страшно было выполнять задание? (цифра)')
        return AWAITING_TASK_FEAR

    context.user_data['emotional_state'] = update.message.text
    sheets.add_user(UserInfo(context.user_data['name'], context.user_data['surname'], context.user_data['phone'],
                             context.user_data['email'], context.user_data['interests'],
                             context.user_data['attend_reason'],
                             context.user_data['expectations'], context.user_data['physical_state'],
                             context.user_data['emotional_state']))
    context.user_data['signed_up'] = True
    update.message.reply_text('Спасибо! Добро пожаловать на марафон!')
    return DUMMY


def handle_dummy(update: Update, context: CallbackContext):
    if context.user_data.get('awaiting_daily_results', False):
        if update.message.text.lower() == 'да':
            update.message.reply_text('Какое задание ты сегодня сделал?', reply_markup=get_tasks_keyboard())
            return AWAITING_TASK_DONE
        elif update.message.text.lower() == 'нет':
            context.user_data['awaiting_daily_results'] = False
            update.message.reply_text('Очень жаль, но, думаю, что в следующие дни у тебя все получится!')
            return DUMMY
        else:
            update.message.reply_text('Я не понимаю. Напиши "да" или "нет"')
            return DUMMY

    update.message.reply_text('К сожалению, я не знаю, что на это ответить')
    return DUMMY


def handle_task_done(update: Update, context: CallbackContext):
    if update.message.text not in sheets.get_today_tasks():
        update.message.reply_text('Такой темы нет у нас в списке, повтори выбор')
        return AWAITING_TASK_DONE

    update.message.reply_text('Как ты себя чувствуешь сейчас на физическом плане? (цифра)')
    return AWAITING_PHYSICAL_STATE


def handle_task_fear(update: Update, context: CallbackContext):
    if not Validator.validate_digit(update.message.text):
        update.message.reply_text('Неверный формат, введи цифру')
        return AWAITING_TASK_FEAR

    update.message.reply_text('Прикрепи ссылку на видео, загруженное в Яндекс.Диск')
    return AWAITING_LINK


def handle_link(update: Update, context: CallbackContext):
    update.message.reply_text('Продолжай в том же духе! Осталось Х дней')
    context.user_data['awaiting_daily_results'] = False
    return DUMMY


def error(update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def stop(update):
    update.message.reply_text('До свидания!')
    return ConversationHandler.END


def morning_reminder(context: CallbackContext):
    chat_id, user_data = context.job.context
    if user_data.get('signed_up', False):
        context.bot.send_message(chat_id, text='Привет, в группе уже выставили задание! '
                                               'Напоминаю, что нужно сдать отчет сегодня до 23:40')


# TODO: obtain topic name once
def daily_results(context: CallbackContext):
    chat_id, user_data = context.job.context
    if user_data.get('signed_up', False):
        user_data['awaiting_daily_results'] = True
        context.bot.send_message(chat_id,
                                 text='У нас сегодня была <название темы>. Ты сделал задание на сегодня?',
                                 reply_markup=YES_NO_KEYBOARD)


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
            AWAITING_TASK_DONE: [MessageHandler(Filters.text, handle_task_done)],
            AWAITING_TASK_FEAR: [MessageHandler(Filters.text, handle_task_fear)],
            AWAITING_LINK: [MessageHandler(Filters.text, handle_link)],
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
