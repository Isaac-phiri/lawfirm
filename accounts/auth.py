import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User  # adjust path to your User model


class JWTAuthenticationFromCookie(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            return None  # DRF will move on to the next auth class

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed('User not found')

        return (user, None)
