from rest_framework import serializers
from api.models import JCHSData

class JCHSDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = JCHSData
        fields = ('id','date','datapoint','datatype','source','valuetype','value')
