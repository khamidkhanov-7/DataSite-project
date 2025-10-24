from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AboutCompanyViewSet

router = DefaultRouter()
router.register(r'about', AboutCompanyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
