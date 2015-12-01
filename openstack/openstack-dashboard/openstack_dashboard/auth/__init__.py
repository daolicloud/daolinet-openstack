from django.conf import settings

from openstack_auth.user import User as BaseUser
from horizon import exceptions


class User(BaseUser):

    def __init__(self, id=None, **kwargs):
        if id is None:
            self.id = getattr(settings, 'ADMIN_TOKEN')
        else:
            self.id = id 

        if not self.id:
            raise exceptions.NotAuthorized("Token not authorized")

        class Token:
            def __init__(self, id):
                self.id = id

        super(User, self).__init__(id=self.id, token=Token(self.id), **kwargs)

    def is_authenticated(self):
        return self.id

    @property
    def authorized_tenants(self):
        return []
