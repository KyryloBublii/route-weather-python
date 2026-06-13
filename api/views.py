from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .service import RoutingService, WeatherService, GeoCodingService
from django.shortcuts import render

def index(request):
    return render(request, 'api/index.html')

@api_view(['GET'])
def get_route_with_weather(request):
    start_city = request.query_params.get('start')
    end_city = request.query_params.get('end')

    if not start_city or not end_city:
        return Response(
            {"error": "start and end query params are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        start = GeoCodingService.get_geocoding(start_city)
        end = GeoCodingService.get_geocoding(end_city)
        route = RoutingService.get_route(start_city, end_city)
        weather_start = WeatherService.get_weather(start_city)
        weather_end = WeatherService.get_weather(end_city)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    return Response({
        "start": {"lat": start["latitude"], "lon": start["longitude"]},
        "end": {"lat": end["latitude"], "lon": end["longitude"]},
        "route": route["routes"][0],
        "weather": {
            "start": weather_start,
            "end": weather_end,
        }
    })