from rest_framework_gis.serializers import GeoFeatureModelSerializer

from rest_framework.serializers import ModelSerializer

from .models import Permit

class PermitSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Permit
        geo_field = 'point'
        fields = '__all__'
