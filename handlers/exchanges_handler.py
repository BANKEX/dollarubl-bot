from mongoengine import Q
from tornkts import utils

from decorator import need_perm
from models.awa import Admin, Exchange
from tornkts.auth import need_role
from tornkts.mixins.auth_mixin import AuthMixin
from tornkts.handlers.object_handler import ObjectHandler


class ExchangesHandler(AuthMixin, ObjectHandler):
    MODEL_CLS = Exchange

    @property
    def queryset(self):
        return Exchange.objects.all().order_by('-creation_date')

    @property
    def auth_classes(self):
        return [Admin]

    @property
    @need_perm([Admin.PERM_EXCHANGES])
    def get_methods(self):
        methods = {'suggest': self.suggest}
        methods.update(super(ExchangesHandler, self).get_methods)
        return methods

    @property
    @need_perm([Admin.PERM_EXCHANGES])
    def post_methods(self):
        return super().post_methods

    @property
    def put_fields(self):
        return {
            'title': {'field_type': 'str'},
            'address': {'field_type': 'str'},
            'phone': {'field_type': 'str'},
            'active': {'field_type': 'bool', 'default': False}
        }

    def get_object(self):
        return super(ExchangesHandler, self).get_object()

    @need_role([Admin.role])
    def info(self):
        self.send_success_response(data={
            'items': [
                self.current_user.to_dict()
            ]
        })

    def save_logic(self, some_object):
        some_object.geo = [self.get_float_argument('lat'), self.get_float_argument('long')]
        some_object.validate_model()
        some_object.save()
        self.send_success_response(data=some_object.to_dict())

    @need_role([Admin.role])
    def suggest(self):
        query = self.get_str_argument('query')
        exchanges = Exchange.objects.filter(Q(title__startswith=query) & Q(active=True)).limit(10)

        suggestions = []
        for exchange in exchanges:
            suggestions.append({
                'data': exchange.get_id(),
                'value': exchange.title
            })

        self.write(utils.json_dumps({'suggestions': suggestions}))
