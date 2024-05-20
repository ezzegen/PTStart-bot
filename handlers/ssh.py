import paramiko
import os
from dotenv import load_dotenv

load_dotenv()


def ssh_connect():
    """
    Подключение к удаленному серверу Linux
    """
    hostname = os.getenv('HOST')
    port = os.getenv('PORT')
    username = os.getenv('USER')
    password = os.getenv('PASSWORD')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, username=username, password=password, port=port)

    return ssh


def execute_command(ssh, command):
    """
    Выполнение команд через ssh-соединение и получение данных
    """
    stdin, stdout, stderr = ssh.exec_command(command)
    output_data = stdout.read().decode('utf-8')
    ssh.close()

    return output_data


if __name__ == '__main__':
    try:
        client = ssh_connect()
        client.close()
        print('Успех! :)')
    except Exception as e:
        print(f'Неуспех: {e} :((!')
