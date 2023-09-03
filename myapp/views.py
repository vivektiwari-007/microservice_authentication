from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from myapp.serializers import *
from myapp.models import *
from rest_framework.permissions import AllowAny
import jwt, string, random
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from twilio.rest import Client
import pycountry
from django.contrib.auth.hashers import make_password
# Create your views here.

class HelloWorldAPIView(ListAPIView):

    def get(self, request, *args, **kwargs):
        return Response({'Message':'Hello world!'},status=status.HTTP_202_ACCEPTED)
    

class RegisterAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            serializer.save()
            user = CustomUser.objects.get(email=email)
            try:
                random_num = random.randint(100000,999999)
                otp = random_num
                from_mail = settings.EMAIL_HOST_USER
                subject = 'Email Verification'
                message = f'you otp is {otp}'
                to = [email]
                send_mail(subject, message, from_mail , to)
                OTP.objects.create(user=user, otp=otp, otp_type="email")
            except:
                return Response({"message":"Invalid email"},status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Send otp on email'}, status=status.HTTP_200_OK)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # email = request['email']

        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            user = CustomUser.objects.filter(email=email).first()
            emailotp = OTP.objects.filter(user=user,otp=otp,otp_type="email").last()
            if emailotp:
                user.mail_verified = True
                user.save()
                emailotp.otp_check = True
                emailotp.save()
                return Response({'message': 'Email Verify Successfully'}, status=status.HTTP_200_OK)
            return Response({'message': 'otp not match'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class BroadCastSMSView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SmsOtpSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            user = CustomUser.objects.get(phone_number=phone_number)
            country_code = serializer.validated_data['country_code']
            contact_number = f"{country_code}{phone_number}"
            randon_num = random.randint(100000,999999)
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(to=contact_number,
                from_=settings.TWILIO_NUMBER,
                body=randon_num
                )
            OTP.objects.create(user=user,otp=randon_num, otp_type="sms")
            return Response({'message': 'Send otp on phone nume'}, status=status.HTTP_200_OK)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.validated_data['otp']
            user = CustomUser.objects.filter(phone_number=phone_number).first()
            phoneotp = OTP.objects.filter(user=user,otp=otp,otp_type="sms").last()
            if phoneotp:
                phoneotp.otp_check = True
                phoneotp.save()
                payload = {
                    'id': user.id,
                    'email': user.email,
                }
                jwt_token = jwt.encode(payload, "SECRET_KEY", algorithm='HS256')
                UserToken.objects.create(user=user, token=jwt_token)
                return Response({"message": "User Login Successfully.",
                                    "results": {'id': user.id, 'email': user.email,'token': jwt_token}},
                                    status=status.HTTP_200_OK)
            return Response({'message': 'otp not match'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class ForgotPasswordAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            user = CustomUser.objects.filter(email=email,mail_verified=True).first()
            if user:
                random_num = random.randint(100000,999999)
                otp = random_num
                subject = "OTP for forgot password"
                message = f'you otp is {otp}'
                to_list = [user.email]
                from_mail = settings.EMAIL_HOST_USER
                rest = send_mail(subject, message, from_mail , to_list)
                OTP.objects.create(user=user, otp=otp, otp_type='passwordreset')
                return Response({'message': 'We have sent you a otp to reset your password'}, status=status.HTTP_200_OK)
            return Response({'message': 'otp not match'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OTPCheckAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = OtpCheckSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            emailotp = OTP.objects.filter(user__email=email,otp=otp).last()
            if emailotp:
                emailotp.otp_check = True
                emailotp.save()
                return Response({'message': 'otp check please set new password'}, status=status.HTTP_200_OK)    
            return Response({'message': 'please enter valid email or otp'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user_obj = CustomUser.objects.filter(email=email,mail_verified=True).last()
            emailotp_obj = OTP.objects.filter(user=user_obj,otp_type='passwordreset').last()
            if user_obj:
                if emailotp_obj.otp_check == True:
                    user_obj.password = make_password(password)
                    user_obj.save()
                    emailotp_obj.delete()
                    OTP.objects.filter(user=user_obj).delete()
                    return Response({'message': 'Successfully set new password'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'please check validate otp to this mail'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'please enter valid email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserEditProfileAPIView(UpdateAPIView):
    serializer_class = UserUpdateProfileSerializer

    def get_object(self, queryset=None):
        print("data",self.request.user)
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(self.object, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            self.object.set_password(request.data.get("password"))
            self.object.save()
            return Response({'message':'Profile update successfully', 
                                    },status=status.HTTP_200_OK)
        return Response({'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



