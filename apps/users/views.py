from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User
from .serializers import UserRegisterSerializer, UserInfoSerializer


class LoginView(APIView):
    """
    POST /api/login/
    请求体：{ "username": "...", "password": "..." }
    返回：{ "access": "...", "refresh": "...", "user": {...} }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response(
                {'detail': '用户名和密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'detail': '用户名或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'detail': '账号已被禁用，请联系管理员'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 生成 JWT Token
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserInfoSerializer(user).data
        })


class UserInfoView(APIView):
    """
    GET /api/user/info/
    返回当前登录用户的基本信息（角色、学院等）
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserInfoSerializer(request.user).data)


class RegisterView(APIView):
    """
    POST /api/register/
    请求体：{ username, password, password_confirm, role, college, email }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'detail': '注册成功',
                    'user': UserInfoSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
