import jwt
from django.contrib.auth import get_user_model
#from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    def decode_handler(self, token):
        User = get_user_model()
        try:
            payload = jwt.decode(
                token,
                self.get_jwt_secret_key(),
                self.verify,
                algorithms=[self.get_jwt_algorithm()]
            )
            user = User.objects.get(pk=payload['user_id'])
            return user
        except (jwt.DecodeError, User.DoesNotExist):
            return None