import logging
import os
from typing import List, Optional, Tuple, Any, Dict, Set
import re

import psycopg2
import paramiko
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from psycopg2 import Error


token = os.environ.get('TOKEN')
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
host = os.environ.get('DB_HOST')
port = os.environ.get('DB_PORT')
database = os.environ.get('DB_DATABASE')


logging.basicConfig(
   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)

logger = logging.getLogger(__name__)


# РАБОТА С БД
def __connect() -> Optional[psycopg2.extensions.connection]:
    """
    Подключение к БД
    """
    try:
        logging.info(f"{os.environ.get('DB_DATABASE')}, {os.environ.get('DB_PORT')}")
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        logging.info("Успешное подключение к БД PostgreSQL")
        return connection
    except (Exception, Error) as error:
        logging.error(f'Ошибка при подключении к PostgreSQL: {error}')
        print(error)


def db_query_handler(query: str) -> List[Tuple[Any, ...]] | None:
    """
    Отработка SQL-запросов
    """
    conn = __connect()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        logging.info(f'Запрос "{query}".')
        if query.startswith('SELECT'):
            rows = cursor.fetchall()
            return rows
    except psycopg2.Error as error:
        logging.error(f"Ошибка при выполнении запроса: {error}")
    finally:
        if conn:
            conn.commit()
            cursor.close()
            conn.close()
            logging.info('Соединение с PostgreSQL закрыто')


# Запросы SQL
def select_query(tabl: str, value: str = '*') -> List[Tuple[Any, ...]]:
    return db_query_handler(f'SELECT {value} FROM {tabl};')


def insert_query(tabl: str, cols: str, value: str) -> None:
    query = f"INSERT INTO {tabl} ({cols}) VALUES ('{value}');"
    return db_query_handler(query)


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f'Привет, {user.full_name}!\nЖми /help для получения списка доступных команд!',
                              reply_markup=ReplyKeyboardMarkup([['/help']], resize_keyboard=True))


def help_command(update, context: CallbackContext):
    """
    Генерация списка доступных команд.
    """
    help_text = "Список доступных команд:\n"
    for handler in list(context.dispatcher.handlers.values())[0]:
        if isinstance(handler, CommandHandler):
            command = handler.command[0]
            help_text += f"/{command}\n"
        else:
            command = handler.entry_points[0].command[0]
            help_text += f"/{command}\n"
    update.message.reply_text(help_text)


# ЗАПРОСЫ НА ВВОД ТЕКСТА
def enter_passwd(update: Update, context: CallbackContext) -> str:
    update.message.reply_text('Введите пароль для проверки: ')
    return 'WAIT_PASSWORD'


def enter_text(update: Update, context: CallbackContext) -> str:
    """
    Запрос текста для поиска номеров телефона / email.
    """
    if update.message.text == '/find_phone_number':
        update.message.reply_text('Введите текст для поиска телефонных номеров: ')
        return 'WAIT_TEXT_PHONE_NUMBERS'
    update.message.reply_text('Введите текст для поиска email: ')
    return 'WAIT_TEXT_EMAIL'


# ОБРАБОТЧИКИ ТЕКСТА
def verify_passwd(update: Update, context: CallbackContext) -> int:
    pattern = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()])(.{8,})$'
    )
    if pattern.match(update.message.text):
        update.message.reply_text('Пароль сложный.')
    else:
        update.message.reply_text('Пароль слишком простой!')
    return ConversationHandler.END


def maker_str(data: Set[str]) -> str:
    """
    Делает результаты поиска удобочитаемыми.
    """
    pretty_string = ''

    for i in range(len(data)):
        pretty_string += f'{i+1}. {list(data)[i]}\n'

    return pretty_string


def find_phone_numbers(update: Update, context: CallbackContext) -> str | int:
    pattern = re.compile(
        r'(?:8|\+7)(?:-|\s)?(?:\(|)?\d{3}(?:\)|)?(?:\s|)?(?:-|\s)?\d{3}(?:-|\s)?\d{2}(?:-|\s)?\d{2}'
    )
    result = set(pattern.findall(update.message.text))

    if not result:
        update.message.reply_text('Телефонные номера не найдены...')
        return ConversationHandler.END

    update.message.reply_text(f'*** Найденные телефонные номера ***\n\n{maker_str(result)}'
                              f'\nХотите записать полученные номера в базу данных?(Y/n)')

    context.user_data.get('phone_numbers_result')
    context.user_data['phone_numbers_result'] = tuple(result)   # Сохранение результата для последующей записи в БД

    return 'WRITE_NUMBER_TO_DB'


def find_email(update: Update, context: CallbackContext) -> str | int:
    pattern = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    result = set(pattern.findall(update.message.text))

    if not result:
        update.message.reply_text('Email-адреса не найдены...')
        return ConversationHandler.END

    update.message.reply_text(f'*** Найденные email-адреса ***\n\n{maker_str(result)}'
                              f'\nХотите записать полученные адреса в базу данных?(Y/n)')

    context.user_data.get('emails_result')
    context.user_data['emails_result'] = tuple(result)

    return 'WRITE_EMAIL_TO_DB'


# ОБРАБОТЧИКИ ЗАПРОСА НА ЗАПИСЬ В БД
def write_pnumber_to_db(update: Update, context: CallbackContext) -> int:
    data = context.user_data['phone_numbers_result']
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


# ОБРАБОТЧИК ЗАПРОСА НА ПОЛУЧЕНИЕ ДАНННЫХ ИЗ БД
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


# ПОЛУЧЕНИЕ ДАННЫХ О СОСТОЯНИИ LINUX-СИСТЕМЫ
commands_dict: Dict[str, str] = {
    '/get_release': ['cat /etc/*release', '*** Информация о релизе ***'],
    '/get_uname': ['uname -a', '*** Информация об архитектуре процессора, имени хоста системы и версии ядра ***'],
    '/get_uptime': ['uptime', '*** Информация о времени работы ***'],
    '/get_df': ['df -h', '*** Информация о состоянии файловой системы ***'],
    '/get_free': ['free -h', '*** Информация о состоянии оперативной памяти ***'],
    '/get_mpstat': ['mpstat', '*** Информация о производительности системы ***'],
    '/get_w': ['w', '*** Информация о работающих в данной системе пользователях ***'],
    '/get_auth': ['last -n 10', '*** Информация о последних 10 входах в систему ***'],
    '/get_critical': ['journalctl -r -p crit -n 5', '*** Информация о последних 5 критических событиях ***'],
    '/get_ps': ['ps aux | head -n 10', '*** Информация о запущенных процессах ***'],
    '/get_ss': ['ss -tuln', '*** Информация об используемых портах ***'],
    '/get_apt_list': ["dpkg-query -l", '*** Информация об установленных пакетах ***'],
    '/get_services': ['systemctl list-units --type=service', '*** Информация о запущенных сервисах ***'],
    '/get_repl_logs': ['tail -n 50 /var/log/postgresql/postgresql.log | grep repl', '*** Логи репликации ***']
}


def __ssh_connect() -> Any:
    """
    Подключение к удаленному серверу Linux
    """
    hostname = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, username=username, password=password, port=port)

    return ssh


def execute_command(ssh, command) -> str:
    """
    Выполнение команд через ssh-соединение и получение данных
    """
    stdin, stdout, stderr = ssh.exec_command(command)
    output_data = stdout.read().decode('utf-8')
    ssh.close()

    return output_data


# ОБРАБОТЧИКИ КОМАНД СОСТОЯНИЯ LINUX_СИСТЕМЫ
def get_sys_info(update: Update, context: CallbackContext) -> None:
    info = commands_dict[update.message.text]
    output_data = f'{info[1]}\n\n{execute_command(__ssh_connect(), info[0])}'
    update.message.reply_text(f'{output_data[:4000]}\n\n...\n Сообщение слишком длинное!'
                              if len(output_data) > 4000 else output_data)


def enter_choice_apt_info(update: Update, context: CallbackContext) -> str:
    """
    Делает запрос на получение данных о пакетах/пакете
    """
    update.message.reply_text('Введите all для отображения всех установленных пакетов '
                              'или наименование интересующего вас пакета: ')
    return 'WAIT_CHOICE_PACKAGE'


def get_apt_info(choice: str) -> str:
    """
    Выцепляет данные о пакетах в зависимости от выбора и формирует удобочитаемый текст
    """
    command = '/get_apt_list'
    info = commands_dict['/get_apt_list']
    if choice == 'all':
        return info[1] + '\n\n' + execute_command(__ssh_connect(), info[0])
    return f'*** Информация о пакете {choice} ***\n\n' + execute_command(__ssh_connect(), f"dpkg -s {choice}")


def get_apt_list(update: Update, context: CallbackContext):
    output_data = get_apt_info(update.message.text)
    if output_data:
        update.message.reply_text(f'{output_data[:4000]}\n\n...\n Сообщение слишком длинное!'
                                  if len(output_data) > 4000 else output_data)
    else:
        update.message.reply_text('Выбранный Вами пакет не установлен!')
    return ConversationHandler.END


def get_logs(update: Update, context: CallbackContext):
    reply = ''
    filename = os.listdir("temp/db_logs/")[0]
    with open("temp/db_logs/"+filename, 'r', encoding='utf-8') as f:
        for i in f:
            if "repl" in i.lower():
                reply += i + '\n'
    update.message.reply_text(reply)


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
    dp.add_handler(CommandHandler('get_repl_logs', get_logs))
    dp.add_handler(CommandHandler('get_phone_numbers', get_info_from_db))
    dp.add_handler(CommandHandler('get_emails', get_info_from_db))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
