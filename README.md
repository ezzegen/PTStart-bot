# PTStart_Bot

## Description

На данном этапе реализован следующий функционал:
- Поиск в тексте телефонных номеров `/find_phone_number` и запись в БД.
- Поиск в тексте email-адресов `/find_email` и запись в БД.
- Проверка сложности пароля `/verify_password`.
- Мониторинг Linux-системы с использованием `paramiko`.
- Просмотр логов репликации `/get_repl_logs`.
- Получение данных из таблицы emails `/get_emails`.
- Получение данных из таблицы phone numbers `/get_phone_numbers`.

Для просмотра доступных команд `/help`.
## Installation
Python 3.10

1. Установка зависимостей:
```
pip install -r requirements.txt
```
2. Создание файла .env

```
HOST = your_hostname
PORT = your_port
USER = your_username
PASSWORD = your_password

TOKEN = your_token

PG_USER = postgres
PG_PASSWORD = your_password
PG_HOST = your_ip_addr_host
PG_PORT = 5432 or your
DB = name_db

```

3. Создание базы данных

```
CREATE DATABASE name_db;
```

## Running the app

```
python main.py
```