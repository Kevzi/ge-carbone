"""
Core app URLs - Authentication and user management
"""
"""
Core app URLs - Authentication and user management
"""
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter
from .views import UserMeView, UserViewSet, ChangePasswordView, CustomTokenObtainPairView
from .superadmin_views import StatsViewSet, GlobalCabinetViewSet, ImpersonationView, GlobalUserViewSet, MLAnalyticsViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'superadmin/cabinets', GlobalCabinetViewSet, basename='superadmin-cabinet')
router.register(r'superadmin/users', GlobalUserViewSet, basename='superadmin-user')
router.register(r'superadmin/analytics', MLAnalyticsViewSet, basename='superadmin-analytics')

urlpatterns = [
    # Authentication
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User
    path('users/me/', UserMeView.as_view(), name='user_me'),
    path('users/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Super Admin
    path('superadmin/stats/', StatsViewSet.as_view({'get': 'list'}), name='superadmin_stats'),
    path('superadmin/impersonate/', ImpersonationView.as_view(), name='superadmin_impersonate'),
    
] + router.urls
