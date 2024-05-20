import re
import sys


def verify_password(password: str) -> str:
    pattern = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()])(.{8,})$'
    )
    if pattern.match(password):
        return 'Пароль сложный.'

    return 'Пароль простой.'


if __name__ == '__main__':
    try:
        assert verify_password('dsfsdf@34ertA') == 'Пароль сложный.'
        assert verify_password('123qwerty') == 'Пароль простой.'
        assert verify_password('dsfsdf@34erta') == 'Пароль простой.'
        print('Все хорошо :)')
    except AssertionError:
        exc_tb = sys.exc_info()[2]
        print(f'Все плохо :(. Ошибка assert в строке: {exc_tb.tb_lineno}')
