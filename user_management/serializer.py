from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers # type: ignore
from django.contrib.auth.forms import PasswordChangeForm
from .models import *



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # depth = 2
        fields = [
            'id',
            'username',
            'email',
            'firstname',
            'lastname',
            'user_active',
            'user_deleted',
            'user_created_at',
            'is_top_admin',
            'is_sp_admin',
            'is_sp_manager',
            'phone',
            'role',
            'password'
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        role_id = validated_data.pop('role', None)  # Get role ID from validated data

        # Retrieve SystemRole instance based on role_id
        if role_id:
            try:
                role_instance = SystemRole.objects.get(id=role_id)
            except SystemRole.DoesNotExist:
                raise serializers.ValidationError("The specified role does not exist.")
        else:
            role_instance = None

        user = User.objects.create_user(**validated_data)

        # Assign the role instance to the user
        user.role = role_instance
        user.save()

        return user


class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        depth = 2


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class SystemPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPermission
        fields = "__all__"
        depth = 2

class SystemRoleSerializer(serializers.ModelSerializer):
    permissions = SystemPermissionSerializer(many=True, read_only=True)
    class Meta:
        model = SystemRole
        fields = "__all__"
        depth = 2

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"