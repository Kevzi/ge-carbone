"""
Core views - User management
"""
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


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
