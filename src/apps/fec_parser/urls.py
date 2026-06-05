from django.urls import path
from .views import FECUploadAPIView

urlpatterns = [
    path('upload/', FECUploadAPIView.as_view(), name='fec-upload'),
]
