import requests
import logging
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado import gen
try:
    import ujson as json
except:
    import json as json

__author__ = 'grigory51'

logger = logging.getLogger('bot')


def get_updates(bot):
    client = AsyncHTTPClient()
    requests.post(bot.get_method_url('setWebhook'))
    update_id = [None]

    @gen.coroutine
    def wrapper():
        data = {}
        if update_id[0] is not None:
            data['offset'] = update_id[0]

        req = HTTPRequest(bot.get_method_url('getUpdates', data))
        res = yield client.fetch(req)

        data = json.loads(res.body)
        if data.get('ok'):
            flag = False
            for item in data.get('result', []):
                flag = True
                if update_id[0] is None or item.get('update_id') + 1 > update_id[0]:
                    update_id[0] = item.get('update_id') + 1
                    bot._on_hook(item)
            if flag:
                logger.debug('Processing updates for %s' % (bot.name,))

    return wrapper
