import re
from django.core.exceptions import FieldDoesNotExist
from django.core.serializers import serialize
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
from django.db.models.expressions import RawSQL
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from api.models import JCHSData, HudPitData, HudHicData, UrbanInstituteRentalCrisisData, Policy, Program, PermitData, TaxlotData
from api.serializers import JCHSDataSerializer, HudPitDataSerializer, HudHicDataSerializer, UrbanInstituteRentalCrisisDataSerializer, PolicySerializer, ProgramSerializer, PermitDataSerializer, TaxlotDataSerializer
from django_filters import rest_framework as filters

def is_valid_table(tbl_name):
    if re.match(r'^[a-z_]*$', tbl_name):
        return True
    return False

# not sure if there is a better way to do this.
class FilterRankedQueryMixin(object):
    @property
    def qs(self):
        """
        Override to nest the ranking query inside of the filters, limiting, and ordering in order to allow for a ranking to be given out of all items, not just those included in the filtering.
        """

        try:
            order_mapping = self.order_mapping
            order_keys = self.order_keys
        except AttributeError:
            order_mapping = None
            order_keys = None

        try:
            ignore_query = self.ignore_query
        except AttributeError:
            ignore_query = None

        filtered = super(FilterRankedQueryMixin, self).qs
        ranked = self._meta.model.objects.with_rank()

        if ignore_query is not None:
            ignore = self._meta.model.objects.filter(datapoint='United States')
            if order_mapping:
                ignore = ignore.annotate(asc_rank=RawSQL('NULL', []), desc_rank=RawSQL('NULL', []), total=RawSQL('NULL', []))
            else:
                ignore = ignore.annotate(rank=RawSQL('NULL', []), total=RawSQL('NULL', []))
            ignore_sql, ignore_params = ignore.query.sql_with_params()
        else:
            ignore_sql = None
            ignore_params = None

        filter_sql, filter_params = filtered.query.sql_with_params()
        parts = filter_sql.split('WHERE')
        if len(parts) > 1:
            filter_part = parts[-1]
            ranked_sql, ranked_params = ranked.query.sql_with_params()

            cnt = filter_sql.count('%s')
            params = ranked_params
            if ignore_params is not None:
                params = params + ignore_params
            if cnt > 0:
                params = params + filter_params[cnt*-1:]
            tbl_name = self._meta.model.objects.model._meta.db_table
            if not is_valid_table(tbl_name):
                raise Exception("Invalid table name: {}".format(tbl_name))

            if ignore_sql is not None:
                ignore_sql = '''UNION ALL
                                {}'''.format(ignore_sql)
            else:
                ignore_sql = ''
            # wrap the ranked list of all items in the filter
            qs = self._meta.model.objects.raw('''
            SELECT * 
            FROM (
                {} 
                {}
            ) AS "{}" 
            WHERE {}
            '''.format(ranked_sql, ignore_sql, tbl_name, filter_part), params)
        else:
            qs = ranked

        l = list(qs)

        if order_mapping and order_keys:
            for obj in l:
                if isinstance(self.order_keys, str):
                    order_key = getattr(obj, self.order_keys)
                else:
                    order_key = tuple(getattr(obj, field) for field in self.order_keys)
                try:
                    order = self.order_mapping[order_key]
                except:
                    #print('No mapping found for {}', order_key)
                    order = 'asc'
                    
                obj.rank = obj.desc_rank if order == 'desc' else obj.asc_rank

        # need to convert to list in order to allow for pagination
        self._qs = l
        return self._qs
     
class JCHSDataFilter(FilterRankedQueryMixin, filters.FilterSet):
    datatype = filters.CharFilter(name='datatype_clean', lookup_expr='icontains')
    datapoint = filters.CharFilter(name='datapoint_clean', lookup_expr='icontains')
    valuetype = filters.CharFilter(name='valuetype_clean', lookup_expr='icontains')
    source = filters.CharFilter(lookup_expr='iexact')

    order_mapping = {
            ('Change in Share of Units by Real Rent Level, 2005–2015, Real Gross Rents Under $800', 'W-16'): 'desc',
            ('Change in Share of Units by Real Rent Level, 2005–2015, Real Gross Rents $2,000 or More', 'W-16'): 'desc',
    }
    order_keys = ('datatype', 'source')
    ignore_query = Q(datapoint='United States')

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

class HudPitDataFilter(FilterRankedQueryMixin, filters.FilterSet):
    datatype = filters.CharFilter(name='datatype_clean')
    datapoint = filters.CharFilter(name='datapoint_clean')
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

class UrbanInstituteRentalCrisisDataFilter(FilterRankedQueryMixin, filters.FilterSet):
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
    new_type = CharInFilter(name='new_type', lookup_expr='in')
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

class TaxlotDataFilter(filters.FilterSet):
    class Meta:
        model = TaxlotData
        fields = ('total_value',)

class TaxlotDataViewSet(viewsets.ModelViewSet):
    queryset = TaxlotData.objects.all()
    serializer_class = TaxlotDataSerializer
    filter_class = TaxlotDataFilter
