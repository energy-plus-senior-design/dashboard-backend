# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import viewsets          # add this
from .serializers import EnergyPredictionSerializer      # add this
from .models import EnergyPrediction                     # add this
from rest_framework.response import Response
from rest_framework.decorators import action
import pickle
import pandas as pd
from django.contrib.staticfiles.templatetags.staticfiles import static
# from django.conf.urls.static import static
from django.conf import settings
import os
import random

class DashView(viewsets.ModelViewSet):       # add this
  serializer_class = EnergyPredictionSerializer          # add this
  queryset = EnergyPrediction.objects.all()              # add this

  @action(detail=False, methods=['POST'], name='Predict Energy')
  def predict(self, request, pk=None):
    # return super().retrieve(request, *args, **kwargs)
    # EnergyPrediction()
    # if request.method == 'GET':
    # print(args)
    # model_path = static('linear_neural_data.sav')
    model_path = "/Users/srinjoymajumdar/software/school/SP19/EE364D/dashboard_backend/static/linear_neural_data.sav"
    linear_model = pickle.load(open(model_path, 'rb'))
    # csv_path = os.path.join(settings.BASE_DIR, static('x_first_row.csv'))
    csv_path = "/Users/srinjoymajumdar/software/school/SP19/EE364D/dashboard_backend/static/x_first_row.csv"
    x = pd.read_csv(csv_path, index_col=0)

    # x["Zone Thermostat Cooling Setpoint Temperature"] = random.uniform(18, 27)
    u = random.uniform(0, 1000)

    # breakpoint()
    filtered = x.filter(regex=r'^Zone Thermostat Heating Setpoint .*.$')
    filtered[:] = request.POST.get("temperature")

    x[filtered.columns] = filtered

    # filtered = x.filter(regex=r'^Zone Thermostat .*.$')
    # filtered[:] = u

    # x[filtered.columns] = filtered

    # filtered = x.filter(regex=r'^Zone Outdoor Air Drybulb Temperature .*.$')
    # filtered[:] = u

    # x[filtered.columns] = filtered

    prediction = linear_model.predict(x)
    # prediction = random.uniform(1, 10)
    return Response({'Electricity:Facility': prediction})