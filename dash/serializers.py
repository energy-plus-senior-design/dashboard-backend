# dash/serializers.py

from rest_framework import serializers
from .models import EnergyPrediction

class EnergyPredictionSerializer(serializers.ModelSerializer):
  class Meta:
    model = EnergyPrediction
    fields = ('electricity_facility',)