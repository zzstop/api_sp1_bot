import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('homework')
handler = RotatingFileHandler(
    filename='homework.log', maxBytes=50000000, backupCount=5)

logging.basicConfig(
    level=logging.DEBUG,
    format=(
        '%(asctime)s, %(levelname)s, %(name)s,'
        '%(funcName)s, %(lineno)d, %(message)s'),
    handlers=(handler,))

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://praktikum.yandex.ru/api/user_api/'
API_METHOD_STATUS_URL = 'homework_statuses/'


def parse_homework_status(homework):
    homework_statuses = {
        'reviewing': 'Работа взята в ревью.',
        'rejected': 'К сожалению в работе нашлись ошибки.',
        'approved': (
            'Ревьюеру всё понравилось,'
            ' можно приступать к следующему уроку.'),
    }
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError:
        raise
    try:
        homework_statuses[homework_status]
    except KeyError:
        raise
    for status, verdict in homework_statuses.items():
        if homework_status == status:
            return (
                'У вас проверили работу'
                f' "{homework_name}"!\n\n{verdict}')


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    data = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        API_URL + API_METHOD_STATUS_URL, headers=headers, params=data)
    return homework_statuses.json()


def send_message(message, bot_client):
    logging.info('Message sent!')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    logging.debug('Bot is running!')
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    #current_timestamp = int(time.time())
    current_timestamp = int(0)
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            existing_homeworks = new_homework.get('homeworks')
            if existing_homeworks:
                send_message(parse_homework_status(
                    existing_homeworks[0]), bot_client)
            current_timestamp = new_homework.get(
                'current_date', int(time.time()))
            time.sleep(300)

        except Exception as e:
            e_message = f'Bot faced an error: {e}.'
            logging.exception(e_message)
            if logging.error(e_message) == logging.exception(e_message):
                bot_client.send_message(chat_id=CHAT_ID, text=e_message)
            time.sleep(5)


if __name__ == '__main__':
    main()
