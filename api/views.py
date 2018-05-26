from django.core.exceptions import FieldDoesNotExist
from django.core.serializers import serialize
from django.contrib.postgres.fields import ArrayField
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from api.models import JCHSData, HudPitData, HudHicData, UrbanInstituteRentalCrisisData, Policy, Program, PermitData
from api.serializers import JCHSDataSerializer, HudPitDataSerializer, HudHicDataSerializer, UrbanInstituteRentalCrisisDataSerializer, PolicySerializer, ProgramSerializer, PermitDataSerializer
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
    queryset = JCHSData.objects.with_rank()
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
        model = HudPitData
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

class PolicyFilter(filters.FilterSet):
    policy_id = filters.CharFilter(lookup_expr='iexact')
    policy_type = filters.CharFilter(name='policy_type_clean', lookup_expr='iexact')
    category = filters.CharFilter(name='category_clean', lookup_expr='iexact')

    class Meta:
        model = Policy
        fields = '__all__'

class ProgramFilter(filters.FilterSet):
    name = filters.CharFilter(name='name_clean', lookup_expr='iexact')
    government_entity = filters.CharFilter(name='government_entity_clean', lookup_expr='iexact')
    policy = filters.CharFilter(name='policy__policy_id', lookup_expr='iexact')

    class Meta:
        model = Program
        fields = '__all__'

class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    filter_class = PolicyFilter
    order_fields = '__all__'

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    filter_class = ProgramFilter
    order_fields = '__all__'

class PermitDataFilter(filters.FilterSet):
    new_class = filters.CharFilter(lookup_expr='iexact')
    new_type = filters.CharFilter(lookup_expr='iexact')
    status = filters.CharFilter(lookup_expr='iexact')
    is_adu = filters.CharFilter(lookup_expr='iexact')
    property_address = filters.CharFilter(lookup_expr='icontains')
    neighborhood = filters.CharFilter(lookup_expr='iexact')
    work_description = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = PermitData
        fields = ('new_class','new_type','status','is_adu','property_address','neighborhood','work_description','year')

class PermitDataViewSet(viewsets.ModelViewSet):
    queryset = PermitData.objects.all()
    serializer_class = PermitDataSerializer
    filter_class = PermitDataFilter

