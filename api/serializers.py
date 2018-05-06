from rest_framework import serializers
from api.models import JCHSData, HudPitData, HudHicData, UrbanInstituteRentalCrisisData

class JCHSDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = JCHSData
        fields = ('id','date','datapoint','datatype','source','valuetype','value')

class HudPitDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HudPitData
        fields = ('id','year','datapoint','datatype','geography','value')

class HudHicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HudHicData
        fields = ('id','year','datapoint','datatype','shelter_status','geography','value')

class UrbanInstituteRentalCrisisDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrbanInstituteRentalCrisisData
        fields = ('id','year','eli_limit','county_fips','county_name','state_name','is_state_data','eli_renters','aaa_units','noasst_units','hud_units','usda_units','no_hud_units','no_usda_units','aaa_units_per_100','noasst_units_per_100','hud_units_per_100','usda_units_per_100','no_hud_units_per_100','no_usda_units_per_100')
