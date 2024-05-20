import re
import sys
from typing import Tuple, List


def finder_email(text: str) -> List[str]:
    pattern = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    result = pattern.findall(text)

    return result


def maker_str(list_of_emails: list) -> str:
    emails = ''
    for i in range(len(list_of_emails)):
        emails += f'{i+1}. {list_of_emails[i]}\n'
    if not emails:
        return 'Email-адреса не найдены...'
    return emails


def text_emails(text) -> Tuple[List[str], str]:
    emails_list = finder_email(text)
    return emails_list, maker_str(emails_list)


if __name__ == '__main__':
    txt = 'Текст для проверки nika@gmail.com jdjjd@gmail@gmail lalala@foo @mail.ru nika2@rambler.ru'
    try:
        assert text_emails(txt) == '1. nika@gmail.com\n2. nika2@rambler.ru\n'
        print('Все хорошо :)')
    except AssertionError:
        exc_tb = sys.exc_info()[2]
        print(f'Все плохо :(. Ошибка assert в строке: {exc_tb.tb_lineno}')
