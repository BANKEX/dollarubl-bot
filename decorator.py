import functools
from tornkts.base.server_response import ServerError


def need_perm(permissions=None):
    if not permissions:
        permissions = []

    def generator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_user or not self.current_user.permissions:
                raise ServerError(ServerError.AUTH_REQUIRED)
            else:
                for item in permissions:
                    if item not in self.current_user.permissions or not self.current_user.permissions[item]:
                        raise ServerError(ServerError.ROLE_FORBIDDEN)
            return method(self, *args, **kwargs)

        return wrapper

    return generator
