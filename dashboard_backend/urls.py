# backend/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from dash import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include(router.urls))
    path('api/<str:modelname>/predict', views.predict)
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)