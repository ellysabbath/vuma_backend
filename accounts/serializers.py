from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 
                  'role', 'is_verified', 'bio', 'skills', 'total_hours', 'joined_date',
                  'profile_picture', 'city', 'region')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                  'phone', 'role', 'date_of_birth', 'gender', 'address', 'city', 'region')
    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_unusable_password()
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 
                  'bio', 'skills', 'availability', 'profile_picture', 'city', 'region')