from handlers.admin_handler import AdminHandler
from handlers.currency_handler import CurrencyHandler
from handlers.exchanges_handler import ExchangesHandler
from handlers.intervals_handler import IntervalsHandler
from handlers.requests_handler import RequestsHandler
from handlers.texts_handler import TextsHandler
from os import path
from handlers.index_handler import IndexHandler
from mongoengine import connection as mongo_connection

from handlers.users_handler import UsersHandler
from periodic import currency_updater, send_fails, rating_request_send
from roboman.server import RobomanServer
from settings import options
from bots.awa_client import AwaClientBot
from bots.awa_exchange import AwaExchangeBot
from bots.kts import KTSBot
from tornado.ioloop import PeriodicCallback, IOLoop
from tornado.web import StaticFileHandler

if __name__ == "__main__":
    bots = [
        #  KTSBot,
        AwaClientBot,
        AwaExchangeBot
    ]

    handlers = [
        (r'/api/(logout)', AdminHandler),
        (r'/api/admin.(.*)', AdminHandler),
        (r'/api/currency.(.*)', CurrencyHandler),
        (r'/api/requests.(.*)', RequestsHandler),
        (r'/api/exchanges.(.*)', ExchangesHandler),
        (r'/api/texts.(.*)', TextsHandler),
        (r'/api/intervals.(.*)', IntervalsHandler),
        (r'/api/users.(.*)', UsersHandler),

        (r'/static/(.*)', StaticFileHandler, dict(path=path.join(options.static_root, 'static'))),
        (r'/(.*)', IndexHandler),
    ]

    settings = {
        'session': {
            'driver': 'file',
            'driver_settings': {
                'host': options.session_path
            },
            'cookie_config': {
                'expires_days': 365
            },
            'force_persistence': True,
            'cache_driver': True
        }
    }

    mongo_connection.connect(host=options.mongo_uri)

    if options.periodic_process:
        PeriodicCallback(currency_updater(True), options.exchange_update_interval).start()
        PeriodicCallback(send_fails, 20 * 1000).start()
        PeriodicCallback(rating_request_send, 20 * 1000).start()

        IOLoop.instance().start()
    else:
        server = RobomanServer(bots=bots, mode=options.mode, handlers=handlers, settings=settings)
        server.start()
