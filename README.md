---
title: Route Weather Python
year: 2026
tags: [python, django, django-rest-framework, openweathermap, docker]
status: complete
cover: photos/main.jpg
---

## What is it

A Django REST API (+ Leaflet frontend) that returns driving route geometry and live weather for both ends of a trip in a single request. The client sends two city names; the server resolves coordinates, fetches the route polyline, and returns weather conditions for origin and destination together in one JSON response.

## Problem it solves

Combining route data and weather data normally requires two separate API calls from the client and two different providers. Route Weather Python does that fan-out on the server, returning a single unified payload so a frontend only needs one request to render a map with weather overlays at each end.

## How it works

- **Frontend:** A Leaflet.js map served at `/` — draws the route polyline and shows weather cards at each endpoint.
- **Backend:** Python 3.14 + Django 6.0 + Django REST Framework 3.17. No database — the app is stateless.
- **Service layer** (`api/service.py`) — three classes, each wrapping a free external API:
  - `GeoCodingService` — Nominatim (OpenStreetMap) `/search`; converts a city name to `(lat, lon)`
  - `RoutingService` — OSRM public routing engine `/route/v1/driving`; returns a full GeoJSON polyline
  - `WeatherService` — OpenWeatherMap `/data/2.5/weather` with `units=metric`; returns city name, temperature (°C), and weather description
- **Endpoint:** `GET /api/route/?start=<city>&end=<city>` — geocodes each city, fetches weather for both, fetches the driving route, and returns a single JSON payload.

### Response shape

```json
{
  "start": { "lat": 50.45, "lon": 30.52 },
  "end":   { "lat": 48.85, "lon": 2.35 },
  "route": { "geometry": { "type": "LineString", "coordinates": [...] }, "distance": 2400000, "duration": 86400 },
  "weather": {
    "start": { "city": "Kyiv", "temperature": 18.4, "description": "Clouds" },
    "end":   { "city": "Paris", "temperature": 22.1, "description": "Clear" }
  }
}
```

## Setup

**Requirements:** Python 3.14, [uv](https://github.com/astral-sh/uv), an [OpenWeatherMap API key](https://openweathermap.org/api).

```bash
# install dependencies
uv sync



# run
uv run python manage.py runserver
```

Open `http://localhost:8000` for the map UI or call the API directly.

## Docker

```bash
docker build -t route-weather .
docker run -p 8000:8000 --env-file .env route-weather
```

## Results

- Single endpoint delivers route geometry plus weather for both cities in one round trip
- No paid mapping SDK required — OSRM and Nominatim are fully open-source and free
- Stateless — no database, no migrations, no runtime state
- Decoupled service layer makes swapping any upstream provider a one-file change
