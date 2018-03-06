# coding=utf-8
from tornado.options import define, options
import os

__author__ = 'grigory51'

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_config(path):
    try:
        options.parse_config_file(path=path, final=False)
    except IOError:
        print('[WARNING] File no readable, run with default settings')


define('host', type=str, group='Server', default='127.0.0.1', help='Listen host')
define('port', type=int, group='Server', default=8080, help='Listen port')
define('server_name', type=str, group='Server', default='https://example.com')
define('session_path', type=str, group='Server', default=CURRENT_DIR + '/runtime/sessions')
define('debug', type=bool, group='Server', default=False, help='Tornado debug mode')
define('config', type=str, group='Server', help='Path to config file', callback=parse_config)
define('runtime', type=str, group='Server', help='Data dir', default=CURRENT_DIR + '/runtime/')
define('static_root', type=str, group='Server', help='Data dir', default=CURRENT_DIR + '/admin/')
define('periodic_process', type=bool, group='Server', default=False)

define('mongo_uri', type=str, group='DB',
       default='mongodb://127.0.0.1:27017/awa?connectTimeoutMS=1000&socketTimeoutMS=1000', help='Connection URI')

define('mode', type=str, group='Bots', default='get_updates')
define('update_interval', type=int, group='Bots', default=1000)
define('key_awa_client', type=str, group='Bots', default='CLIENT_API_KEY')
define('key_awa_exchange', type=str, group='Bots', default='EXCHANGE_API_KEY')

define('enable_testing_question', type=bool, default=True)

define('exchange_update_interval', type=int, group='Bots', default=30 * 60 * 1000)

options.parse_command_line(final=True)
