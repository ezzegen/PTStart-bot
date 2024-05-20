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

1. Создание файла .env
Обратите внимание, что в данном случае прописаны стандартные значения DB_REPL_USER и DB_REPL_PASSWORD, для тестирования работы репликации менять их не рекомендуется (иначе придется менять значения в init.sql) 
```
TOKEN = your_token

DB_USER = postgres
DB_PASSWORD = your_password
DB_HOST = db
DB_PORT = 5432
DB_DATABASE = your DB name

RM_HOST = your host for monitoring
RM_USER = user name
RM_PASSWORD = your_password
RM_PORT = 22

DB_REPL_USER = repl_user
DB_REPL_PASSWORD = Qq12345
DB_REPL_HOST = db_repl
DB_REPL_PORT = 5432
```
2. Установка необходимых утилит на Linux-серверах.
```
Убедитесь, что на хосте для мониторинга установлен сервис ssh и утилита mpstat,
а на хосте для развертывания приложения установлены docker, docker-compose!
```
3. Сборка и запуск образов

```
docker-compose up --build
```
## Running the app

```
docker-compose start
```