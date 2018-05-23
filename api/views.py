from django.core.exceptions import FieldDoesNotExist
from django.contrib.postgres.fields import ArrayField
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from api.models import JCHSData, HudPitData, HudHicData, UrbanInstituteRentalCrisisData
from api.serializers import JCHSDataSerializer, HudPitDataSerializer, HudHicDataSerializer, UrbanInstituteRentalCrisisDataSerializer
from django_filters import rest_framework as filters

class JCHSDataFilter(filters.FilterSet):
    datatype = filters.CharFilter(name='datatype_clean', lookup_expr='icontains')
    datapoint = filters.CharFilter(name='datapoint_clean', lookup_expr='icontains')
    valuetype = filters.CharFilter(name='valuetype_clean', lookup_expr='icontains')
    source = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = JCHSData
        fields = ['datatype', 'datapoint', 'valuetype', 'source', 'date']

class JCHSDataViewSet(viewsets.ModelViewSet):
    queryset = JCHSData.objects.all()
    serializer_class = JCHSDataSerializer
    filter_class = JCHSDataFilter
    ordering_fields = '__all__'

    @list_route()
    def meta(self, request):
        fields = request.data.get('fields') if request.data else request.query_params.get('fields')
        if fields is None:
            fields = ['datatype','datapoint','valuetype','source','date']
        elif isinstance(fields, str):
            fields = [fields]

        results = {}
        for f in fields:
            try:
                clean_field = JCHSData._meta.get_field(f + '_clean')
            except FieldDoesNotExist:
                results[f] = self.queryset.values_list(f, flat=True).distinct().order_by(f)
            else:
                values = self.queryset.values_list(f, clean_field.name).distinct(f).order_by(f)
                values = [ { 'value': v[0], 'value_clean': v[1] } for v in values ]
                results[f] = values

        result = {
            'results': results
        }

        return Response(result)

class HudPitDataFilter(filters.FilterSet):
    datatype = filters.CharFilter(name='datatype_clean', lookup_expr='icontains')
    datapoint = filters.CharFilter(name='datapoint_clean', lookup_expr='icontains')
    geography = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = HidPitData
        fields = ['datatype','datapoint','geography','year']

class HudPitDataViewSet(viewsets.ModelViewSet):            
    queryset = HudPitData.objects.all()
    serializer_class = HudPitDataSerializer
    filter_class = HudPitDataFilter
    ordering_fields = '__all__'

class HudHicDataFilter(filters.FilterSet):
    class Meta:
        model = HudHicData
        fields = '__all__'
        filter_overrides = {
            ArrayField: {
                'filter_class': filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }

class HudHicDataViewSet(viewsets.ModelViewSet):            
    queryset = HudHicData.objects.all()
    serializer_class = HudHicDataSerializer
    filter_class = HudHicDataFilter
    ordering_fields = '__all__'

class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class UrbanInstituteRentalCrisisDataFilter(filters.FilterSet):
    county_name__in = CharInFilter(name='county_name', lookup_expr='in')
    county_fips__in = CharInFilter(name='county_fips', lookup_expr='in')
    county_name = filters.CharFilter(lookup_expr='iexact')
    state_name = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = UrbanInstituteRentalCrisisData
        fields = '__all__'

class UrbanInstituteRentalCrisisDataViewSet(viewsets.ModelViewSet):            
    queryset = UrbanInstituteRentalCrisisData.objects.all()
    serializer_class = UrbanInstituteRentalCrisisDataSerializer
    filter_class = UrbanInstituteRentalCrisisDataFilter
    ordering_fields = '__all__'
