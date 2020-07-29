import logging
import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://praktikum.yandex.ru/api/user_api/{method}/'
bot = telegram.Bot(token=TELEGRAM_TOKEN)

available_statuses = {
    "approved": 'Ревьюеру всё понравилось, можно приступать к следующему уроку.',
    "rejected": 'К сожалению в работе нашлись ошибки.'
}


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status in available_statuses:
        verdict = available_statuses[homework_status]
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else:
        raise KeyError(f'Несуществующий статус {homework_status}')


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses_url = API_URL.format(method='homework_statuses')
    try:
        homework_statuses = requests.get(
            homework_statuses_url,
            headers=headers,
            params=params
        )
        return homework_statuses.json()
    except Exception as e:
        logging.exception(f'Произошла ошибка {e}')
        return {}


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            logging.exception(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
