# services/amadeus_client.py
import httpx
from config import AMADEUS_API_KEY, AMADEUS_API_SECRET

AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_API_BASE_URL = "https://test.api.amadeus.com"

class AmadeusClient:
    def __init__(self):
        self._api_key = AMADEUS_API_KEY
        self._api_secret = AMADEUS_API_SECRET
        self._access_token = None
        self._client = httpx.AsyncClient()

    async def _get_access_token(self):
        """Fetches a new access token from Amadeus."""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = f"grant_type=client_credentials&client_id={self._api_key}&client_secret={self._api_secret}"
        
        try:
            response = await self._client.post(AMADEUS_TOKEN_URL, headers=headers, content=body)
            response.raise_for_status()
            self._access_token = response.json()["access_token"]
            return self._access_token
        except httpx.HTTPStatusError as e:
            print(f"Error getting Amadeus token: {e.response.text}")
            return None

    async def _make_request(self, url: str, params: dict):
        """Makes an authenticated request to the Amadeus API."""
        if not self._access_token:
            await self._get_access_token()
            if not self._access_token:
                return "Failed to authenticate with Amadeus."

        headers = {"Authorization": f"Bearer {self._access_token}"}
        try:
            response = await self._client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Retry once
            if e.response.status_code == 401:
                print("Token expired, refreshing...")
                await self._get_access_token()
                headers["Authorization"] = f"Bearer {self._access_token}"
                response = await self._client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            print(f"Amadeus API Error: {e.response.text}")
            return {"error": f"API request failed with status {e.response.status_code}"}

    async def get_city_code(self, city_name: str) -> str | None:
        """Gets the IATA city code required by other Amadeus endpoints."""
        url = f"{AMADEUS_API_BASE_URL}/v1/reference-data/locations/cities"
        params = {"keyword": city_name.upper(), "max": 1}
        data = await self._make_request(url, params)
        if data and data.get("data"):
            return data["data"][0]["iataCode"]
        return None
    # Hotels by city
    async def find_hotels(self, city_code: str) -> str:
        """Finds hotels in a given city."""
        url = f"{AMADEUS_API_BASE_URL}/v1/reference-data/locations/hotels/by-city"
        params = {"cityCode": city_code, "radius": 20, "ratings": "4,5"}
        data = await self._make_request(url, params)
        if not data or not data.get("data"):
            return "Could not find any 4 or 5-star hotels for that city."
        else:   
            # Format the data for the LLM
            hotels_summary = "🏨 Top 10 Hotels Nearby:\n"
            hotel_list = data.get("data", []) if isinstance(data, dict) else []
            for hotel in hotel_list[:10]:  # ✅ limit to 10
                name = hotel.get("name", "Unknown Hotel")
                distance = hotel.get("distance", {}).get("value", "N/A")
                unit = hotel.get("distance", {}).get("unit", "km")
                hotels_summary += f"• {name} — {distance} {unit} away\n"

        
       
        print("Extracted hotels Summary:",hotels_summary)
        return f"Found these top-rated hotels:\n{hotels_summary}"
    
    async def get_city_coordinates(self, city_name: str) -> tuple[float, float]:
        """
        Search for city info by name and return (latitude, longitude).
        Uses Amadeus API endpoint:
        GET /reference-data/locations/cities
        with parameters: keyword, max=1
        """
        url = f"{AMADEUS_API_BASE_URL}/v1/reference-data/locations/cities"
        params = {
            "keyword": city_name,
            "max": 1,
                      
        }
        data = await self._make_request(url, params)
        
        if not data or not data.get("data"):
            return "Could not find city coordinates."
        
        
        if data.get("data") and len(data["data"]) > 0:
            geo_code = data["data"][0].get("geoCode", {})
            lat = geo_code.get("latitude", 0.0)
            lon = geo_code.get("longitude", 0.0)
            print("City Coordinates:", lat, lon)
            return lat, lon
        
    async def find_points_of_interest(self, latitude: float, longitude: float) -> str:
        """Finds points of interest near a city center."""
        
        url = f"{AMADEUS_API_BASE_URL}/v1/shopping/activities/by-square"
        params = {
            "north": latitude + 0.05,
            "south": latitude - 0.05,
            "east": longitude + 0.05,
            "west": longitude - 0.05,
            
        }

        data = await self._make_request(url,params )
        if not data or not data.get("data"):
            return "Could not find any major points of interest for that city."
        else:
            attractions_summary = "\n📍 Top 10 Tourist Attractions:\n"
            poi_list = data.get("data", []) if isinstance(data, dict) else []
            for poi in poi_list[:10]:  # ✅ limit to 10
                 name = poi.get("name", "Unknown Attraction")
                 category = poi.get("category", "N/A")
                 attractions_summary += f"• {name} ({category})\n"

        print("Extracted POI summary:",attractions_summary)
        return f"Found these popular attractions:\n{attractions_summary}"

# Create a single instance to be used across the app
amadeus_client = AmadeusClient()