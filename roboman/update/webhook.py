from tornkts import utils
from tornkts.base.server_response import ServerError
from tornkts.handlers import BaseHandler

__author__ = 'grigory51'


class WebHookHandler(BaseHandler):
    def post(self, id):
        bots = self.settings.get('bots', [])
        ok = False
        for bot in bots:
            if bot.access_key == id:
                ok = True
                data = utils.json_loads(self.request.body)
                bot._on_hook(**data)
                break
        if ok:
            self.send_success_response()
        else:
            raise ServerError('not_found')
