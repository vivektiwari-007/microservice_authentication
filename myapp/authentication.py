from rest_framework.authentication import TokenAuthentication, get_authorization_header
from myapp.models import CustomUser
from rest_framework import status, exceptions
import jwt


class MyLoginTokenAuthentications(TokenAuthentication):
    model = None

    def get_model(self):
        return CustomUser

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = "Invalid token header. no creadential provided"
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)
        
        try:
            token = auth[1]
            if token == "null":
                msg = "Null token not allowed"
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = "Invalid token header. token string should not contain Invalid characters"
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        model = self.get_model()
        try:
            payload = jwt.decode(token, "SECRET_KEY", algorithms="HS256")
            email = payload['email']
            userid = payload['id']
            try:
                user = CustomUser.objects.get(email=email, id=userid, is_active=True)
            except:
                msg = {'Error':'User not found','status':'400'}
                raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = {'Error':"Error code signature", 'status':'403'}
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            msg = {'Error': "Token is Invalid", 'status':'403'}
            raise exceptions.AuthenticationFailed(msg)
        print(user)
        print(token)
        return (user, token)

    def authenticate_header(self, request):
        return 'Token'


