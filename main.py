import logging
import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from psycopg2 import Error

from handlers.phone_number import text_phone_numbers
from handlers.emails import text_emails
from handlers.password import verify_password
from handlers.linux_monitoring import get_info, get_apt_info
from db.db_connect import create_tables
from db.db_query import select_query, insert_query


load_dotenv()
token = os.getenv('TOKEN')

logging.basicConfig(
    filename='app_log.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    create_tables()

    update.message.reply_text(f'Привет {user.full_name}!')


def help_command(update, context: CallbackContext):
    help_text = "Список доступных команд:\n"
    for handler in list(context.dispatcher.handlers.values())[0]:
        if isinstance(handler, CommandHandler):
            command = handler.command[0]
            help_text += f"/{command}\n"
        else:
            command = handler.entry_points[0].command[0]
            help_text += f"/{command}\n"
    update.message.reply_text(help_text)


def enter_passwd(update: Update, context: CallbackContext) -> str:
    update.message.reply_text('Введите пароль для проверки: ')
    return 'WAIT_PASSWORD'


def verify_passwd(update: Update, context: CallbackContext) -> int:
    check_password = verify_password(update.message.text)
    update.message.reply_text(check_password)
    return ConversationHandler.END


def enter_text(update: Update, context: CallbackContext) -> str:
    """
    Запрос текста для поиска номеров телефона / email.
    """
    if update.message.text == '/find_phone_number':
        update.message.reply_text('Введите текст для поиска телефонных номеров: ')
        return 'WAIT_TEXT_PHONE_NUMBERS'
    update.message.reply_text('Введите текст для поиска email: ')
    return 'WAIT_TEXT_EMAIL'


def find_phone_numbers(update: Update, context: CallbackContext) -> str | int:
    numbers_lst, phone_numbers_str = text_phone_numbers(update.message.text)
    if not numbers_lst:
        update.message.reply_text(phone_numbers_str)
        return ConversationHandler.END

    update.message.reply_text(f'*** Найденные телефонные номера ***\n\n{phone_numbers_str}'
                              f'\nХотите записать полученные номера в базу данных?(Y/n)')

    context.user_data.get('phone_numbers_result')
    context.user_data['phone_numbers_result'] = tuple(numbers_lst)   # Сохранение результата для последующей записи в БД

    return 'WRITE_NUMBER_TO_DB'


def find_email(update: Update, context: CallbackContext) -> str | int:
    emails_lst, email_addresses_str = text_emails(update.message.text)
    if not emails_lst:
        update.message.reply_text(email_addresses_str)
        return ConversationHandler.END

    update.message.reply_text(f'*** Найденные email-адреса ***\n\n{email_addresses_str}'
                              f'\nХотите записать полученные адреса в базу данных?(Y/n)')

    context.user_data.get('emails_result')
    context.user_data['emails_result'] = tuple(emails_lst)

    return 'WRITE_EMAIL_TO_DB'


def write_pnumber_to_db(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'y':
        try:
            for number in context.user_data['phone_numbers_result']:
                insert_query('phone_numbers', 'number', number)
            update.message.reply_text('Данные успешно сохранены!')
        except (Exception, Error) as error:
            logging.error(f"Ошибка при сохранении данных: {error}")
            update.message.reply_text('Не удалось сохранить данные!')
    else:
        update.message.reply_text('Хорошо, данные сохранять не будем :).')
    return ConversationHandler.END


def write_email_to_db(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'y':
        try:
            for email in context.user_data['emails_result']:
                insert_query('emails', 'email_address', email)
            update.message.reply_text('Данные успешно сохранены!')
        except (Exception, Error) as error:
            logging.error(f"Ошибка при сохранении данных: {error}")
            update.message.reply_text('Не удалось сохранить данные!')
    else:
        update.message.reply_text('Хорошо, данные сохранять не будем :).')
    return ConversationHandler.END


def get_info_from_db(update: Update, context: CallbackContext) -> None:
    tabl = 'phone_numbers'
    if update.message.text == '/get_emails':
        tabl = 'emails'
    data = select_query(tabl)
    if data:
        pretty_str = ''.join((f'{n}. {d}\n' for n, d in data))
        update.message.reply_text(f'*** Данные из таблицы {tabl} ***\n\n{pretty_str}')
    else:
        update.message.reply_text(f'Таблица {tabl} пустая.')


def get_sys_info(update: Update, context: CallbackContext) -> None:
    output_data = get_info(update.message.text)
    update.message.reply_text(f'{output_data[:4000]}\n\n...\n Сообщение слишком длинное!'
                              if len(output_data) > 4000 else output_data)


def enter_choice_apt_info(update: Update, context: CallbackContext) -> str:
    update.message.reply_text('Введите all для отображения всех установленных пакетов'
                              'или наименование интересующего вас пакета: ')
    return 'WAIT_CHOICE_PACKAGE'


def get_apt_list(update: Update, context: CallbackContext) -> int:
    output_data = get_apt_info(update.message.text)
    if output_data:
        update.message.reply_text(f'{output_data[:4000]}\n\n...\n Сообщение слишком длинное!'
                                  if len(output_data) > 4000 else output_data)
    else:
        update.message.reply_text('Выбранный Вами пакет не установлен!')
    return ConversationHandler.END


def main():
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    conv_handler_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', enter_text)],
        states={
            'WAIT_TEXT_PHONE_NUMBERS': [MessageHandler(Filters.text & ~Filters.command, find_phone_numbers)],
            'WRITE_NUMBER_TO_DB': [MessageHandler(Filters.text, write_pnumber_to_db)],
        },
        fallbacks=[]
    )

    conv_handler_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', enter_text)],
        states={
            'WAIT_TEXT_EMAIL': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'WRITE_EMAIL_TO_DB': [MessageHandler(Filters.text, write_email_to_db)],
        },
        fallbacks=[]
    )

    conv_handler_verify_passwd = ConversationHandler(
        entry_points=[CommandHandler('verify_password', enter_passwd)],
        states={
            'WAIT_PASSWORD': [MessageHandler(Filters.text & ~Filters.command, verify_passwd)],
        },
        fallbacks=[]
    )

    conv_handler_get_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', enter_choice_apt_info)],
        states={
            'WAIT_CHOICE_PACKAGE': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(conv_handler_phone_number)
    dp.add_handler(conv_handler_email)
    dp.add_handler(conv_handler_verify_passwd)
    dp.add_handler(CommandHandler('get_release', get_sys_info))
    dp.add_handler(CommandHandler('get_uname', get_sys_info))
    dp.add_handler(CommandHandler('get_uptime', get_sys_info))
    dp.add_handler(CommandHandler('get_df', get_sys_info))
    dp.add_handler(CommandHandler('get_free', get_sys_info))
    dp.add_handler(CommandHandler('get_mpstat', get_sys_info))
    dp.add_handler(CommandHandler('get_w', get_sys_info))
    dp.add_handler(CommandHandler('get_auth', get_sys_info))
    dp.add_handler(CommandHandler('get_critical', get_sys_info))
    dp.add_handler(CommandHandler('get_ps', get_sys_info))
    dp.add_handler(CommandHandler('get_ss', get_sys_info))
    dp.add_handler(CommandHandler('get_services', get_sys_info))
    dp.add_handler(conv_handler_get_apt_list)
    dp.add_handler(CommandHandler('get_repl_logs', get_sys_info))
    dp.add_handler(CommandHandler('get_phone_numbers', get_info_from_db))
    dp.add_handler(CommandHandler('get_emails', get_info_from_db))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
