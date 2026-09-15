from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6, label='密码')
    password_confirm = serializers.CharField(write_only=True, label='确认密码')

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'role', 'college', 'email']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次密码不一致'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    """用户信息序列化器（用于 /user/info/ 接口）"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'role_display', 'college']
