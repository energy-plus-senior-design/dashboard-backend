# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import EnergyPrediction
# Register your models here.

class EnergyPredictionAdmin(admin.ModelAdmin):  # add this
  list_display = ('electricity_facility',) # add this

# Register your models here.
admin.site.register(EnergyPrediction, EnergyPredictionAdmin) # add this