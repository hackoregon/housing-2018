from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from api.models import JCHSData, HudPitData, HudHicData, UrbanInstituteRentalCrisisData, Policy, Program, PermitData

class JCHSDataSerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField()
    total = serializers.IntegerField()

    class Meta:
        model = JCHSData
        fields = ('id','date','datapoint','datatype','source','valuetype','value','rank','total')

class HudPitDataSerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField()
    total = serializers.IntegerField()

    class Meta:
        model = HudPitData
        fields = ('id','year','datapoint','datatype','geography','value','rank','total')

class HudHicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HudHicData
        fields = ('id','year','datapoint','datatype','shelter_status','geography','value')

class UrbanInstituteRentalCrisisDataSerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField()
    total = serializers.IntegerField()

    class Meta:
        model = UrbanInstituteRentalCrisisData
        fields = ('id','year','eli_limit','county_fips','county_name','state_name','is_state_data','eli_renters','aaa_units','noasst_units','hud_units','usda_units','no_hud_units','no_usda_units','aaa_units_per_100','noasst_units_per_100','hud_units_per_100','usda_units_per_100','no_hud_units_per_100','no_usda_units_per_100','rank','total')

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ('policy_id','policy_type','description','category','link1','link1_name','link2','link2_name','link3','link3_name')

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ('policy','name','description','government_entity','year_implemented','link1','link1_name','link2','link2_name','link3','link3_name')

class PermitDataSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PermitData
        geo_field = 'point'
        fields = ('in_date','issue_date','status','year','new_class','new_type','neighborhood','is_adu','pdx_bnd','property_address','work_description','new_units','valuation')
