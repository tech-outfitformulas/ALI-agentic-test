import requests
from typing import Dict, Any, Optional

class WeatherService:
    @staticmethod
    def get_coordinates(city_name: str) -> Optional[Dict[str, float]]:
        """Get latitude and longitude for a city name."""
        try:
            url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data and data["results"]:
                result = data["results"][0]
                return {
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "name": result["name"],
                    "country": result.get("country", "")
                }
            return None
        except Exception as e:
            print(f"Error fetching coordinates: {e}")
            return None

    @staticmethod
    def get_current_weather(city_name: str) -> Dict[str, Any]:
        """Fetch current weather for a city."""
        coords = WeatherService.get_coordinates(city_name)
        if not coords:
            return {"error": "City not found"}

        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "current": ["temperature_2m", "weather_code"],
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            weather_code = current.get("weather_code", 0)
            
            # Simple WMO code interpretation
            condition = "Unknown"
            if weather_code == 0: condition = "Clear sky"
            elif weather_code in [1, 2, 3]: condition = "Partly cloudy"
            elif weather_code in [45, 48]: condition = "Foggy"
            elif weather_code in [51, 53, 55]: condition = "Drizzle"
            elif weather_code in [61, 63, 65]: condition = "Rain"
            elif weather_code in [71, 73, 75]: condition = "Snow"
            elif weather_code >= 95: condition = "Thunderstorm"
            
            return {
                "location": f"{coords['name']}, {coords['country']}",
                "temperature": f"{current.get('temperature_2m')}°F",
                "conditions": condition,
                "source": "Open-Meteo"
            }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return {"error": "Weather service unavailable"}
