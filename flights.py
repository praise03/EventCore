### Write code for the new module here and import it from agent.py.
import aiohttp
import asyncio
import requests
from dotenv import load_dotenv
import os

# Load environment variables from the .env file (if present)
load_dotenv()

AMADEUS_CLIENT = os.getenv("AMADEUS_CLIENT")
AMADEUS_SECRET = os.getenv("AMADEUS_SECRET")

AUTH_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {"grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT,
        "client_secret": AMADEUS_SECRET}
response = requests.post(AUTH_ENDPOINT,
                        headers=headers,
                        data=data)
access_token = response.json()['access_token']

async def fetch_offers(l_from, to, date):
    headers = {'Authorization': 'Bearer' + ' ' + access_token}
    flight_search_endpoint = 'https://test.api.amadeus.com/v2/shopping/flight-offers'
    parameters = {"adults": 1, "originLocationCode":l_from, "destinationLocationCode":to,"departureDate":date, "max":2}

    async with aiohttp.ClientSession() as session:
        async with session.get(flight_search_endpoint,params=parameters,headers=headers) as resp:
            flights = await resp.json()
            # print(flights)
            return flights

def simplify_flight_offers(response_data):
    """
    Reduce response.data to a list of simplified dicts with only essential fields.
    Each offer includes: id, price (total + currency), total_duration, total_stops,
    seats, and a list of segments with key details (carrierCode, number, departure,
    arrival, duration, stops, aircraft).
    """
    simplified = []
    for offer in response_data:
        if offer['type'] != 'flight-offer':
            continue

        price = offer['price']
        itinerary = offer['itineraries'][0]  # Assume single outbound itinerary

        # Simplified segments list
        segments = []
        total_stops = 0
        for seg in itinerary['segments']:
            stops = seg['numberOfStops']
            total_stops += stops
            stops_info = seg.get('stops', []) if stops > 0 else []

            segments.append({
                'carrierCode': seg['carrierCode'],
                'number': seg['number'],
                'departure': {
                    'iataCode': seg['departure']['iataCode'],
                    'at': seg['departure']['at']
                },
                'arrival': {
                    'iataCode': seg['arrival']['iataCode'],
                    'at': seg['arrival']['at']
                },
                'duration': seg['duration'],
                'stops': stops_info,  # List of stop dicts if any
                'aircraft': seg['aircraft']['code']
            })

        simplified.append({
            'id': offer['id'],
            'price': {
                'total': price['total'],
                'currency': price['currency']
            },
            'total_duration': itinerary['duration'],
            'total_stops': total_stops,
            'seats': offer['numberOfBookableSeats'],
            'segments': segments
        })

    return simplified
