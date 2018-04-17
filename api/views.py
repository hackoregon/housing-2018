from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from api.models import JCHSData
from api.serializers import JCHSDataSerializer

class JCHSDataViewSet(viewsets.ModelViewSet):
    queryset = JCHSData.objects.all()
    serializer_class = JCHSDataSerializer
#filter_backends = (,)
    search_fields = '__all__'
    filter_fields = '__all__'
    ordering_fields = '__all__'

    @list_route()
    def meta(self, request):
        fields = request.data.get('fields') if request.data else request.query_params.get('fields')
        if fields is None:
            fields = ['datatype','datapoint','valuetype','source','date']
        elif isinstance(fields, str):
            fields = [fields]

        result = {
            'results': { f: self.queryset.values_list(f, flat=True).distinct().order_by(f) for f in fields }
        }

        return Response(result)

            

