from .models import CustomUser, UserProfile, Address
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        
class UserWithProfileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'
        
class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['contact_no', 'username', 'password', 'email', 'role']
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["email"] = user.email
        token["role"] = user.role

        association = getattr(user, "association", None)

        token["association_id"] = str(association.id) if association else None
        token["association_name"] = association.name if association else None
        token["association_barangay"] = association.barangay if association else None

        return token
        
    def validate(self, attrs):
        data = super().validate(attrs)
        association = getattr(self.user, "association", None)

        data.update({
            "user_id": str(self.user.id),
            "email": self.user.email,
            "role": self.user.role,
            "username": self.user.username,
            "association": {
                "id": str(association.id) if association else None,
                "name": association.name if association else None,
                "barangay": association.barangay if association else None,
            }
        })
        
        print(data)
        
        return data

    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'region',
            'province',
            'city',
            'barangay',
            'street_address',
            'postal_code',
            'landmark',
        ]