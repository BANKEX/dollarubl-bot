from decorator import need_perm
from models.awa import Admin
from tornkts.auth import need_role
from tornkts.mixins.auth_mixin import AuthMixin
from tornkts.handlers.object_handler import ObjectHandler


class AdminHandler(AuthMixin, ObjectHandler):
    MODEL_CLS = Admin

    @property
    def auth_classes(self):
        return [Admin]

    @property
    def put_fields(self):
        return {
            'email': {'field_type': 'email'},
            'name': {'field_type': 'str'},
            'password': {'field_type': 'str', 'require_if_none': True, 'hash': True, 'length_min': 8}
        }

    @property
    def post_methods(self):
        methods = {
            'auth': self.auth,
            'logout': self.logout,
        }
        methods.update(super().post_methods)
        return methods

    @property
    def get_methods(self):
        methods = {
            "info": self.info
        }
        methods.update(super(AdminHandler, self).get_methods)
        return methods

    @need_perm([Admin.PERM_ADMINS])
    def get_object(self):
        return super(AdminHandler, self).get_object()

    @need_role([Admin.role])
    def info(self):
        self.send_success_response(data={'items': [self.current_user.to_dict()]})

    @need_perm([Admin.PERM_ADMINS])
    def save_logic(self, some_object):
        some_object.permissions = {}
        for key in ['admins', 'users', 'currencies', 'requests', 'exchanges', 'texts', 'intervals']:
            some_object.permissions[key] = self.get_bool_argument(key, default=False)
        some_object.save()
        self.send_success_response(data=some_object.to_dict())

    @need_perm([Admin.PERM_ADMINS])
    def logout(self):
        self.session_destroy()
        self.send_success_response()

    @need_perm([Admin.PERM_ADMINS])
    def save_object(self):
        return super().save_object()

    @need_perm([Admin.PERM_ADMINS])
    def delete_object(self):
        return super().delete_object()