from rest_framework import viewsets
from api.models import JCHSData
from api.serializers import JCHSDataSerializer

class JCHSDataViewSet(viewsets.ModelViewSet):
    queryset = JCHSData.objects.all()
    serializer_class = JCHSDataSerializer
#filter_backends = (,)
    search_fields = '__all__'
    filter_fields = '__all__'
    ordering_fields = '__all__'

