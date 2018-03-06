from tornkts.base.mongodb import get_object_or_none
from tornkts.base.server_response import ServerError

from bots.awa_exchange import AwaExchangeBot
from content.awa_client import STEP_NO_RESPONSE
from decorator import need_perm
from models.awa import Admin, Currency, Request, Exchange
from tornkts.auth import need_role
from tornkts.mixins.auth_mixin import AuthMixin
from tornkts.handlers.object_handler import ObjectHandler

from periodic import send_fails


class RequestsHandler(AuthMixin, ObjectHandler):
    MODEL_CLS = Request

    @property
    def queryset(self):
        return Request.objects.all().order_by('-creation_date')

    @property
    @need_perm([Admin.PERM_REQUESTS])
    def get_methods(self):
        return super().get_methods

    @property
    @need_perm([Admin.PERM_REQUESTS])
    def post_methods(self):
        methods = {
            'setFail': self.set_fail,
            'respond': self.respond,
            'updateDateCommissionWithdrawal': self.update_date_commission_withdrawal,
            'updateExchangeConfirm': self.update_exchange_confirm
        }
        methods.update(super(RequestsHandler, self).post_methods)
        return methods

    @property
    def auth_classes(self):
        return [Admin]

    def get_object(self):
        return super(RequestsHandler, self).get_object()

    def info(self):
        self.send_success_response(data={
            'items': [
                self.current_user.to_dict()
            ]
        })

    def set_fail(self):
        id = self.get_mongo_id_argument('id')
        request = get_object_or_none(self.MODEL_CLS, id=id)
        if request is None:
            raise ServerError(ServerError.NOT_FOUND)
        else:
            send_fails([request])

        self.send_success_response()

    def respond(self):
        request_id = self.get_mongo_id_argument('request_id')
        exchange_id = self.get_mongo_id_argument('exchange_id')
        external_id = self.get_int_argument('external_id')

        request = get_object_or_none(Request, id=request_id)
        if request is None:
            raise ServerError(ServerError.NOT_FOUND)
        exchange = get_object_or_none(Exchange, id=exchange_id)
        if exchange is None:
            raise ServerError(ServerError.NOT_FOUND)

        AwaExchangeBot._confirm(request=request, exchange=exchange, external_id=external_id)

    def update_date_commission_withdrawal(self):
        id = self.get_mongo_id_argument('id')
        request = get_object_or_none(Request, id=id)
        if request is None:
            raise ServerError(ServerError.NOT_FOUND)

        value = self.get_date_argument('value', '%d.%m.%Y')
        request.update(date_commission_withdrawal=value)

        self.send_success_response()

    def update_exchange_confirm(self):
        id = self.get_mongo_id_argument('id')
        request = get_object_or_none(Request, id=id)
        if request is None:
            raise ServerError(ServerError.NOT_FOUND)

        value = self.get_bool_argument('value')
        request.update(exchange_confirm=value)

        self.send_success_response()
