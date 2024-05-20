import re
import sys
from typing import Tuple, List


def finder_phone_number(text: str) -> List[str]:
    pattern = re.compile(
        r'(?:8|\+7)(?:-|\s)?(?:\(|)?\d{3}(?:\)|)?(?:\s|)?(?:-|\s)?\d{3}(?:-|\s)?\d{2}(?:-|\s)?\d{2}'
    )
    result = pattern.findall(text)

    return result


def maker_str(list_of_phones: list) -> str:
    phone_numbers = ''
    for i in range(len(list_of_phones)):
        phone_numbers += f'{i+1}. {list_of_phones[i]}\n'
    if not phone_numbers:
        return 'Телефонные номера не найдены...'
    return phone_numbers


def text_phone_numbers(text) -> Tuple[List[str], str]:
    phone_numbers_list = finder_phone_number(text)
    return phone_numbers_list, maker_str(phone_numbers_list)


if __name__ == '__main__':
    txt = 'Текст для проверки 88002000801, 3-400-500-9-09, +7 (917) 124-08-99!'
    try:
        assert text_phone_numbers(txt) == '1. 88002000801\n2. +7 (917) 124-08-99\n'
        assert text_phone_numbers('Текст для проверки') == 'Телефонные номера не найдены...'
        assert (finder_phone_number(
            '+79171280604, +7(917)1240899, +7 950 777 68 75\\'
            '+7 927 800 55 44, +7 (950) 777 68 75, +7-988-765-88-00\\'
            '89171280604, 8(917)1240899, 8 950 777 68 75\\'
            '8 927 800 55 44, 8 (950) 777 68 75, 8-988-765-88-00\\'
        )
                == [
                    '+79171280604', '+7(917)1240899', '+7 950 777 68 75',
                    '+7 927 800 55 44', '+7 (950) 777 68 75', '+7-988-765-88-00',
                    '89171280604', '8(917)1240899', '8 950 777 68 75',
                    '8 927 800 55 44', '8 (950) 777 68 75', '8-988-765-88-00'
                ]
                )
        print(finder_phone_number(txt))
        print(text_phone_numbers(txt))
        print('Все хорошо :)')
    except AssertionError:
        exc_tb = sys.exc_info()[2]
        print(f'Все плохо :(. Ошибка assert в строке: {exc_tb.tb_lineno}')
