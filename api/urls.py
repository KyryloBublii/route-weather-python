from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/route/', views.get_route_with_weather, name='get_route'),
]