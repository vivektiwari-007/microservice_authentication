from django.urls import path, include
from myapp.views import *

urlpatterns = [
    path('', HelloWorldAPIView.as_view() , name="helloview"),
    path('register/', RegisterAPIView.as_view() , name="register"),
    path('verify_email/', VerifyEmail.as_view() , name="verify_email"),
    path('sms_otp/', BroadCastSMSView.as_view() , name="sms_otp"),
    path('login/', LoginAPIView.as_view() , name="login"),
    path('forget_password/', ForgotPasswordAPIView.as_view() , name="forget_password"),
    path('otpcheck/', OTPCheckAPIView.as_view() , name="otpcheck"),
    path('setnewpassword/', SetNewPasswordAPIView.as_view() , name="setnewpassword"),
    path('updateprofile/', UserEditProfileAPIView.as_view() , name="updateprofile"),
]
