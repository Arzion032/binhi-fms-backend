from rest_framework import serializers
from .models import Farmer, Association

class AssociationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Association
        fields = '__all__'


class FarmerSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Farmer
        fields = '__all__'
        read_only_fields = ['id', 'date_registered', 'updated_at', 'age']

    def get_age(self, obj):
        return obj.age
