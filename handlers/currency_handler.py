from decorator import need_perm
from models.awa import Admin, Currency
from tornkts.auth import need_role
from tornkts.mixins.auth_mixin import AuthMixin
from tornkts.handlers.object_handler import ObjectHandler


class CurrencyHandler(AuthMixin, ObjectHandler):
    MODEL_CLS = Currency

    @property
    def auth_classes(self):
        return [Admin]

    @property
    def put_fields(self):
        return {
            'code': {'field_type': 'str'},
            'value': {'field_type': 'float'},
            'direct': {'field_type': 'str'},
            'use_api': {'field_type': 'bool', 'default': False}
        }

    @need_perm([Admin.PERM_CURRENCIES])
    def get_object(self):
        return super(CurrencyHandler, self).get_object()

    @property
    @need_perm([Admin.PERM_CURRENCIES])
    def get_methods(self):
        return super().get_methods

    @property
    @need_perm([Admin.PERM_CURRENCIES])
    def post_methods(self):
        return super().post_methods
