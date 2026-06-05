"""
Core views - User management
"""
from rest_framework import generics, permissions
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
