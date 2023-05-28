import requests
from printing import __print

__author__ = 'dutch_pool'

telegram_conf = {}


def set_telegram_conf(telegram_configuration):
    global telegram_conf
    telegram_conf = telegram_configuration


# telegram
def __send_telegram_message(message):
    try:
        if not telegram_conf["use_telegram"]:
            return

        uri = "https://api.telegram.org/bot" + telegram_conf["bot_key"] + "/sendMessage"
        if len(message) < 2000:
            response = requests.post(uri, json={
                "chat_id": telegram_conf["chat_id"],
                "text": message,
                "parse_mode": "HTML"
            })
            if not response.ok:
                print(response.status_code, response.text)
        else:
            chunks = int(len(message) / 2000) + 1
            for i in range(0, chunks):
                response = requests.post(uri, json={
                    "chat_id": telegram_conf["chat_id"],
                    "text": message[i * chunks: (i + 1) * chunks],
                    "parse_mode": "HTML"
                })
                if not response.ok:
                    print(response.status_code, response.text)
    except Exception as e:
        __print('Unable to send telegram message.')
        print(e)
