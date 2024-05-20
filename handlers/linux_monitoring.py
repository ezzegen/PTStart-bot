from handlers.ssh import ssh_connect, execute_command
from typing import Dict


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
    '/get_apt_list': ["apt list  | awk '{print $1}'", '*** Информация об установленных пакетах ***'],
    '/get_services': [f'sudo service --status-all | grep "+"', '*** Информация о запущенных сервисах ***'],
    '/get_repl_logs': ['tail -n 50 /var/log/postgresql/postgresql-15-main.log | grep "repl"', '*** Логи репликации ***']
}


def get_info(command: str) -> str:
    info = commands_dict[command]
    return f'{info[1]}\n\n{execute_command(ssh_connect(), info[0])}'


def get_apt_info(choice: str) -> str:
    command = '/get_apt_list'
    info = f'*** Информация о пакете {choice} ***'
    if choice == 'all':
        return get_info(command)
    return info + '\n\n' + execute_command(ssh_connect(), f'dpkg -s {choice}')


if __name__ == '__main__':
    try:
        print(get_apt_info('apt'))
        print(get_info('/get_services'))
        print('Успех! :)')
    except Exception as e:
        print(f'Неудача: {e} :( !')
