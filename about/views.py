from rest_framework import viewsets
from .models import AboutCompany
from .serializers import AboutCompanySerializer

class AboutCompanyViewSet(viewsets.ModelViewSet):
    queryset = AboutCompany.objects.all().order_by('-created_at')
    serializer_class = AboutCompanySerializer
