from rest_framework import serializers
from myapp.models import CustomUser

class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('first_name','last_name','phone_number','email','password','user_type')

    def validate_email(self, email):
        existing = CustomUser.objects.filter(email=email).first()
        if existing:
            raise serializers.ValidationError("Email already exist")
        return email

    def create(self, validate_data):
        password = validate_data.pop('password', None)
        instance = self.Meta.model(**validate_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()


class SmsOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    country_code = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
    


class ForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email',)


class OtpCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()


class SetNewPasswordSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ('email','password')


class UserUpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('first_name','last_name','phone_number','password')

