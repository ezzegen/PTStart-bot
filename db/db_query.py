from typing import List, Tuple, Any
from db.db_connect import db_query_handler


def select_query(tabl: str, value: str = '*') -> List[Tuple[Any, ...]]:
    return db_query_handler(f'SELECT {value} FROM {tabl};')


def insert_query(tabl: str, cols: str, value: str) -> None:
    query = f"INSERT INTO {tabl} ({cols}) VALUES ('{value}');"
    return db_query_handler(query)


def delete_query(tabl: str, id: int) -> None:
    query = f"DELETE FROM {tabl} WHERE id = {id};"
    return db_query_handler(query)


if __name__ == '__main__':
    insert_query('emails', 'email_address', 'test@gmail.com')
    delete_query('emails', 5)
    data = select_query('emails')
    for row in data:
        print(row)
