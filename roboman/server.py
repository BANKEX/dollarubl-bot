import requests
from roboman.bot import BaseBot
from roboman.update.get_updates import get_updates
from roboman.update.webhook import WebHookHandler
from tornkts.base.server_response import ServerError
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornkts.handlers import DefaultHandler
from tornado.ioloop import PeriodicCallback
from settings import options

__author__ = 'grigory51'


class RobomanServer(Application):
    def __init__(self, **kwargs):
        bots = kwargs.get('bots')
        mode = kwargs.get('mode', BaseBot.MODE_HOOK)

        handlers = []

        if mode == BaseBot.MODE_HOOK:
            handlers += [
                (r"/telegram.(\w+)", WebHookHandler),
            ]

        if isinstance(bots, list):
            for bot in kwargs.get('bots'):
                handlers += (r"/{0}.(\w+)".format(bot.name), bot),
        else:
            bots = []

        settings = {
            'compress_response': False,
            'default_handler_class': DefaultHandler,
            'debug': options.debug,
            'bots': bots,
            'mode': mode
        }

        handlers += kwargs.get('handlers', [])
        settings.update(kwargs.get('settings', {}))
        super(RobomanServer, self).__init__(handlers, **settings)

    def start(self):
        bots = self.settings.get('bots', [])
        mode = self.settings.get('mode', BaseBot.MODE_HOOK)

        for bot in bots:
            if mode == BaseBot.MODE_HOOK:
                requests.post(bot.get_method_url('setWebhook'), {'url': bot.get_webhook_url()})
            elif mode == BaseBot.MODE_GET_UPDATES:
                PeriodicCallback(get_updates(bot), options.update_interval).start()
            else:
                raise ServerError(ServerError.INTERNAL_SERVER_ERROR, description='Bad server mode')

        self.listen(options.port, options.host)
        IOLoop.instance().start()
