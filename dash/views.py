# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import viewsets          # add this
from .serializers import EnergyPredictionSerializer      # add this
from .models import EnergyPrediction                     # add this
from rest_framework.response import Response
from rest_framework.decorators import api_view
import pickle
import pandas as pd
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import Http404, HttpResponseBadRequest
from django.conf import settings
from keras.models import load_model
from django.views.decorators.csrf import csrf_exempt
from keras import backend as K
import tensorflow as tf
import numpy as np

import json
import os
import random

@csrf_exempt
@api_view(['POST'])
def predict(request, pk=None, modelname=None):
  if request.method != 'POST':
    raise Http404("Route only defined for POST requests.")

  if modelname is None:
    raise HttpResponseBadRequest("Model name not provided")

  response_functions = {
    "explicit-rnn": explicit_rnn,
    "implicit-rnn": implicit_rnn,
    "hybrid": hybrid
  }

  try:
    return response_functions[modelname](request)
  except KeyError:
    raise HttpResponseBadRequest("Model name malformed")

def hybrid(request):
  with tf.Session(graph=tf.Graph()) as sess:
    K.set_session(sess)

    base_path = "/Users/srinjoymajumdar/software/school/SP19/EE364D/dashboard_backend/static/hybrid"
    model = load_model(f'{base_path}/hybrid_2019-11-12_2.h5')

    ut_row = pickle.load(open(f'{base_path}/u_real.pickle', 'rb')).loc[[4378]]
    user_ut_dict = request.POST

    for var_name, value in user_ut_dict.items():
      for zone_name in ut_row[var_name]:
          ut_row.loc[4378, (var_name, zone_name)] = make_float(value)

    scalerU = pickle.load(open(f'{base_path}/hybrid_2019-11-12_2_scalerU.pickle', 'rb'))
    testX = format_u_for_implicit_rnn(ut_row, scalerU)

    prediction = model.predict(testX)[0][0]

    # scalerY = pickle.load(open(f'{base_path}/hybrid_2019-11-12_2_scalerY.pickle', 'rb'))
    # electricity_usage = scalerY.inverse_transform(prediction)[0][0]

    electricity_usage = prediction
    return Response({'Electricity:Facility': electricity_usage})

def explicit_rnn(request):
  with tf.Session(graph=tf.Graph()) as sess:
    K.set_session(sess)

    base_path = "/Users/srinjoymajumdar/software/school/SP19/EE364D/dashboard_backend/static/explicit_rnn"
    model = load_model(f'{base_path}/train_10-18_test_19.h5')

    ut_row = pickle.load(open(f'{base_path}/u_real.pickle', 'rb')).loc[[4378]]
    user_ut_dict = request.POST

    for var_name, value in user_ut_dict.items():
      for zone_name in ut_row[var_name]:
          ut_row.loc[4378, (var_name, zone_name)] = make_float(value)

    scaler_y = pickle.load(open(f'{base_path}/scalery.pickle', 'rb'))
    prediction = model.predict(ut_row)
    # breakpoint()
    # electricity_usage = scaler_y.inverse_transform(prediction[0][48:50].reshape(-1, 1))[0]
    electricity_usage = prediction[0][49]
    return Response({'Electricity:Facility': electricity_usage})

def implicit_rnn(request):
  with tf.Session(graph=tf.Graph()) as sess:
    K.set_session(sess)

    base_path = "/Users/srinjoymajumdar/software/school/SP19/EE364D/dashboard_backend/static/implicit_rnn"
    model = load_model(f'{base_path}/implicit_rnn_2019-11-11.h5')

    ut_row = pickle.load(open(f'{base_path}/implicit_rnn_2019-11-11_u_real-4.pickle', 'rb')).iloc[[4378]]
    user_ut_dict = request.POST

    for var_name, value in user_ut_dict.items():
      for zone_name in ut_row[var_name]:
          ut_row.loc[4388, (var_name, zone_name)] = make_float(value)

    scalerU = pickle.load(open(f'{base_path}/implicit_rnn_2019-11-11_scalerU.pickle', 'rb'))
    testX = format_u_for_implicit_rnn(ut_row, scalerU)

    prediction = model.predict(testX)

    # scalerY = pickle.load(open(f'{base_path}/implicit_rnn_2019-11-11_scalerY.pickle', 'rb'))
    # electricity_usage = scalerY.inverse_transform(prediction)[0][0]
    electricity_usage = prediction[0][0]
    return Response({'Electricity:Facility': electricity_usage})

def make_float(num):
  num = num.replace(' ','').replace(',','.').replace("−", "-")
  return float(num)

# # for implicit rnn
def format_u_for_implicit_rnn(u_orig_df, scalerU):
  base_path = "/Users/srinjoymajumdar/software/school/SP19/EE364D/dashboard_backend/static/implicit_rnn"
  u_orig = u_orig_df.values
  u_t = scalerU.transform(u_orig)

  u_trainset_repeat = u_t[:, np.newaxis, :]
  u_trainset_repeat = np.repeat(u_trainset_repeat, 1, axis=1)
  return u_trainset_repeat
