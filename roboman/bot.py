import json
import traceback
import requests
from tornado.httputil import url_concat
from tornkts.handlers import BaseHandler
from settings import options
import random
import string
import logging

__author__ = 'grigory51'

logger = logging.getLogger('bot')


class BaseBot(BaseHandler):
    MODE_HOOK = 'hook'
    MODE_GET_UPDATES = 'get_updates'

    name = None
    key = None
    access_key = None

    connection = requests.Session()

    def __init__(self, application, request, **kwargs):
        super(BaseBot, self).__init__(application, request, **kwargs)

    @classmethod
    def _on_hook(cls, data):
        message = data.get('message')
        if isinstance(message, dict):
            user = message.get('from', {})

            payload = {
                'text': message.get('text'),
                'date': message.get('date'),

                'chat_id': message.get('chat', {}).get('id', None),
                'chat_title': message.get('chat', {}).get('title', None),

                'from_id': user.get('id', None),
                'from_username': user.get('username', None),
                'from_first_name': user.get('first_name', None),
                'from_last_name': user.get('last_name', None),

                'location': message.get('location', None),
                'photo': message.get('photo', None)
            }

            try:
                cls.on_hook(payload)
            except Exception as e:
                logger.exception(e)

    @classmethod
    def match_command(cls, command, text):
        if text is None or command is None:
            return False

        text = text.strip()
        if text.startswith(command):
            text = text[len(command):]
            text = text.strip()
            return {
                'result': True,
                'args': [i for i in text.split(' ')]
            }
        return False

    @classmethod
    def send(cls, **params):
        res = cls.connection.post(cls.get_method_url('sendMessage'), params=params)
        if res.status_code != 200:
            logger.error(res.text)

    @classmethod
    def sendLocation(cls, **params):
        res = cls.connection.post(cls.get_method_url('sendLocation'), params=params)
        if res.status_code != 200:
            logger.error(res.text)

    @classmethod
    def get_method_url(cls, method, params=None):
        url = 'https://api.telegram.org/bot' + cls.key + '/' + method
        if params is not None:
            url = url_concat(url, params)
        return url

    @classmethod
    def get_file_url(cls, path, params=None):
        return 'https://api.telegram.org/file/bot' + cls.key + '/' + path

    @classmethod
    def get_webhook_url(cls):
        cls.access_key = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(30)])
        return options.server_name + '/telegram.' + cls.access_key
