from decorator import need_perm
from models.awa import Admin, User
from tornkts.auth import need_role
from tornkts.mixins.auth_mixin import AuthMixin
from tornkts.handlers.object_handler import ObjectHandler


class UsersHandler(AuthMixin, ObjectHandler):
    MODEL_CLS = User

    @property
    def queryset(self):
        return User.objects.all().order_by('-creation_date')

    @property
    def auth_classes(self):
        return [Admin]

    @need_role([Admin.role])
    def get_object(self):
        return super(UsersHandler, self).get_object()

    @property
    @need_perm([Admin.PERM_REQUESTS])
    def get_methods(self):
        return super().get_methods

    @property
    @need_perm([Admin.PERM_REQUESTS])
    def post_methods(self):
        return super().post_methods