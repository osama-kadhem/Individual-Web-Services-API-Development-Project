import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

async def get_current_weather(city: str) -> Optional[Dict[str, Any]]:
    """
    Fetches current weather data for a given city from OpenWeatherMap.
    Returns None if the API key is invalid or city not found.
    """
    if settings.OPENWEATHER_API_KEY == "your_openweather_key_here":
        # Mock weather for demonstration if no key is provided
        return {
            "temp": 32.5,  # Force heat stress mock
            "humidity": 85.0,
            "description": "mocked heatwave",
            "is_mock": True
        }

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return {
                    "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                    "is_mock": False
                }
    except Exception as e:
        print(f"Weather API Error: {e}")
    
    return None
