from decorator import need_perm
from models.awa import Admin
from tornkts.auth import need_role
from tornkts.mixins.auth_mixin import AuthMixin
from tornkts.handlers.object_handler import ObjectHandler
from models.content import Interval


class IntervalsHandler(AuthMixin, ObjectHandler):
    MODEL_CLS = Interval

    @property
    @need_perm([Admin.PERM_INTERVALS])
    def get_methods(self):
        methods = {'keys': self.keys}
        methods.update(super(IntervalsHandler, self).get_methods)
        return methods

    @property
    @need_perm([Admin.PERM_INTERVALS])
    def post_methods(self):
        return super().post_methods

    @property
    def queryset(self):
        return Interval.objects.all().order_by('key')

    @property
    def auth_classes(self):
        return [Admin]

    @property
    def put_fields(self):
        return {
            'key': {'field_type': 'str'},
            'value': {'field_type': 'str'},
            'comment': {'field_type': 'str'}
        }

    @need_role([Admin.role])
    def get_object(self):
        return super(IntervalsHandler, self).get_object()

    @need_role([Admin.role])
    def keys(self):
        self.send_success_response(data=Interval.defaults().keys())
