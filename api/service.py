import requests
from django.conf import settings
from django.core.cache import cache


class WeatherService:
    @staticmethod
    def get_weather(city: str) -> dict:
        cache_key = f"weather_{city.lower()}"
        cached = cache.get(cache_key)

        if cached:
            return cached

        response = requests.get(
            settings.WEATHER_API_URL,
            params={
                'q': city,
                'cnt': 1,
                'units': 'metric',
                'appid': settings.WEATHER_API_KEY
            }
        )
        response.raise_for_status()

        data = response.json()

        result = {
            'city': data["name"],
            'temperature': data["main"]["temp"],
            'description': data["weather"][0]['main']
        }

        cache.set(cache_key, result, timeout=60*10)  # 10 minutes
        return result

class RoutingService:
    OSRM_URL = "http://router.project-osrm.org/route/v1/driving"
    @staticmethod
    def get_route(start_location: str, finish_location: str ) -> dict:
        start_data = GeoCodingService.get_geocoding(start_location)
        finish_data = GeoCodingService.get_geocoding(finish_location)

        url = f"{RoutingService.OSRM_URL}/{start_data['longitude']},{start_data['latitude']};{finish_data['longitude']},{finish_data['latitude']}"

        params = {"overview": "full", "geometries": "geojson"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()


class GeoCodingService:
    NOMINATIM_URL="https://nominatim.openstreetmap.org/search"
    @staticmethod
    def get_geocoding(city: str) -> dict:
        cache_key = f"geocode_{city.lower()}"
        cached = cache.get(cache_key)

        if cached:
            return cached

        response = requests.get(
            GeoCodingService.NOMINATIM_URL,
            params={
                'q': city,
                'format': 'json',
                'limit': 1
            },
            headers={
                'User-Agent': 'route-weather-app'
            }
        )
        response.raise_for_status()

        data = response.json()

        if not data:
            raise Exception('No results found')

        result = {
            'longitude': float(data[0]["lon"]),
            'latitude': float(data[0]["lat"]),
        }

        cache.set(cache_key, result, timeout=60*60)  # 1 hour

        return result