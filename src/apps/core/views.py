"""
Core views - User management
"""
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer, ChangePasswordSerializer
from rest_framework import status

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
