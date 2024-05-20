import os
import logging
from dotenv import load_dotenv

import psycopg2
from psycopg2 import Error
from typing import List, Optional, Tuple, Any

load_dotenv()


def __connect() -> Optional[psycopg2.extensions.connection]:
    try:
        connection = psycopg2.connect(
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT'),
            database=os.getenv('DB')
        )
        logging.info("Успешное подключение к БД PostgreSQL")
        return connection
    except (Exception, Error) as error:
        logging.error(f'Ошибка при работе с PostgreSQL: {error}')


def create_tables() -> None:
    conn = __connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS emails ('
            'ID SERIAL PRIMARY KEY,'
            'email_address VARCHAR(100) NOT NULL);'
        )
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS phone_numbers ('
            'ID SERIAL PRIMARY KEY,'
            'number VARCHAR(30) NOT NULL);'
        )
        logging.info(f'Создание таблиц.')
        conn.commit()
    except (Exception, Error) as error:
        logging.error(f"Ошибка при создании таблиц: {error}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            logging.info('Соединение с PostgreSQL закрыто')


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


if __name__ == '__main__':
    insert = db_query_handler("INSERT INTO emails (email_address) VALUES ('nika@gmail.com'), ('test@mail.com'), ('pt-start@pt.ru')")
    data = db_query_handler('SELECT * FROM emails;')

    if data:
        for row in data:
            print(row)
