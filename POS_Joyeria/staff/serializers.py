from rest_framework import serializers
from .models import StaffProfile

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = "__all__"
