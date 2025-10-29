"""
This module integrates with the Amadeus API to authenticate, retrieve, and process hotel data
based on proximity to event locations. It manages OAuth2 authentication, makes asynchronous and
synchronous API calls to fetch hotel details, filters
and simplifies hotel offers for readability, and can also retrieve sentiment data for specific
hotels. Overall, it serves as a utility for discovering and evaluating nearby accommodations,
streamlining the process of finding relevant hotels for event attendees.
"""

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
access_token = response.json()["access_token"]


async def fetch_hotels_by_proximity(event):
    d_longitude = -58.43
    d_latitude = -34.62

    b_longitude = 54.37
    b_latitude = 24.4539

    headers = {'Authorization': 'Bearer' + ' ' + access_token}
    hotel_search_endpoint = 'https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-geocode'
    parameters = {}
    if event == "devconnect":
        parameters = {"latitude": d_latitude, "longitude": d_longitude, "radius": 3, "radiusUnit": "KM",
                      "hotelSource": "ALL"}
    elif event == "breakpoint":
        parameters = {"latitude": b_latitude, "longitude": b_longitude, "radius": 3, "radiusUnit": "KM",
                      "hotelSource": "ALL"}

    async with aiohttp.ClientSession() as session:
        async with session.get(hotel_search_endpoint, params=parameters, headers=headers) as resp:
            hotels = await resp.json()
            return hotels


def fetch_hotel_data():
    try:
        # Search hotel offers by city code (e.g., BUE for Buenos Aires)
        response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode='BUE'  # Buenos Aires; use 'EZE' for airport-focused
        )

        venue_lat, venue_lon = -34.6037, -58.3816  # your venue

        filtered_hotels = []
        for hotel in response.data:
            geo = hotel.get("geoCode", {})
            lat, lon = geo.get("latitude"), geo.get("longitude")

            if lat and lon:
                distance = haversine(venue_lat, venue_lon, lat, lon)
                if distance <= 5:  # within 5 km
                    hotel["distance_from_venue_km"] = round(distance, 2)
                    filtered_hotels.append(hotel)

        print(f"{len(filtered_hotels)} hotels within 5 km of venue.")

        for h in filtered_hotels[:1]:
            name = h.get("name", "Unknown Hotel")
            dist = h.get("distance_from_venue_km", "?")

            address_data = h.get("address", {})
            address_lines = address_data.get("lines", [])
            city = address_data.get("cityName", "")
            address = ", ".join(address_lines + [city]) if address_lines else city

            rating = h.get("rating", "N/A")
            contact = h.get("contact", {})
            phone = contact.get("phone", "N/A")
            email = contact.get("email", "N/A")

            amenities = h.get("amenities", [])
            if isinstance(amenities, list):
                amenities_preview = ", ".join(amenities[:5])  # show top 5 amenities
            else:
                amenities_preview = "N/A"

            # If offers exist (for prices)
            price_info = "N/A"
            offers = h.get("offers")
            if offers and isinstance(offers, list):
                offer = offers[0]
                price = offer.get("price", {}).get("total")
                currency = offer.get("price", {}).get("currency")
                if price and currency:
                    price_info = f"{price} {currency}"

            print(f" 🏨 {name}")
            print(f" 📍 Address: {address}")
            print(f" 📍 Distance from venue: {dist} km")
            print(f" ⭐ Rating: {rating}")
            print(f" 💰 Price (sample): {price_info}")
            print(f" 📞 Contact: {phone} | {email}")
            print(f" 🛎️ Amenities: {amenities_preview}")
            print("  — — — — — — — — — — — — — — —")

        print(simplify_hotel_offers(response.data))
        # global data
        # data = simplify_hotel_offers(response.data)
        # print(asyncio.run(extract_hotel_data(data)))

    except ResponseError as error:
        raise error


def simplify_hotel_offers(response_data):
    """Reduce to: id, name, price (total/currency), rating, location, availability."""
    simplified = []
    for hotel in response_data:
        if 'hotel' in hotel:
            h = hotel['hotel']
            offers = hotel.get('offers', [{}])[0]  # First offer
            price = offers.get('price', {})
            simplified.append({
                'id': h['hotelId'],
                'name': h['name'],
                'price': {
                    'total': price.get('total', 'N/A'),
                    'currency': price.get('currency', 'EUR')
                },
                'rating': h.get('rating', 'N/A'),  # e.g., 4.2/5
                'location': {
                    'address': h['address']['addressLine'],  # Street
                    'city': h['address']['cityName'],
                    'iataCode': h.get('iataCode', 'BUE')  # Proximity
                },
                'availability': offers.get('rateCode', 'Available')  # Or check 'soldOut'
            })
    # Sort by price ascending
    simplified.sort(key=lambda x: float(x['price']['total']) if x['price']['total'] != 'N/A' else float('inf'))
    return simplified[:3]  # Top 3


# Usage: hotel_data = simplify_hotel_offers(response.data)


def fetch_hotel_sentiment(hotel_id: str):
    try:
        response = amadeus.e_reputation.hotel_sentiments.get(hotelIds=hotel_id)
        print(response.data)
        if response.data != None:
            return response.data
        else:
            return "We Couldnt fetch and additional info about this hotel"
    except ResponseError as error:
        raise error
