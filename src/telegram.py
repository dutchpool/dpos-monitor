from urllib.parse import urlparse

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

        uri = urlparse(
            'https://api.telegram.org/bot' + telegram_conf["bot_key"] + '/sendMessage?text=' + message + '&chat_id=' +
            telegram_conf["chat_id"]
        ).geturl()
        requests.get(uri)
    except Exception as e:
        __print('Unable to send telegram message.')
        print(e)