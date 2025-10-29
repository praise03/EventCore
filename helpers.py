"""
This module serves as the AI-powered natural language processing layer for the event assistant
system. It uses the ASI1 API to interpret and classify user prompts into categories like flights,
weather, hotels, currency, or event info, and to generate structured or enriched responses.
Each helper function handles a specific type of query — for example, parsing flight data, summarizing
weather forecasts, formatting hotel results, interpreting currency conversions, or answering general
event-related enquiries. Essentially, it bridges raw user input with intelligent, structured outputs
that other agents in the system can act upon.
"""

import requests, os
import json

asi1_api_key = "sk_d2913a2aa0d74896a958c6af8dcb0494e7cea7053fb945f1904f0452a307ed96"

ASI1_Endpoint = "https://api.asi1.ai/v1/chat/completions"

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {asi1_api_key}'  # agentverse api key; stored in agent secrets
}


async def categorize_prompt(prompt):
    payload = json.dumps({
        "model": "asi1-mini",
        "messages": [
            {
                "role": "system",
                "content": """
                        You are a hyper-efficient prompt classifier that ruthlessly categorizes prompts from user messages with machine-like precision.
                         Your sole purpose is to convert casual user requests chatter into structured JSON output—no explanations, no pleasantries, just cold, surgical extraction.
                          When a user inputs a prompt you classify it into 1 of 5 categories i.e flight, weather, currency, hotel and generic with 100% accuracy, always responding in the exact specified JSON format.
                            No emojis, no markdown, just raw structured data ready for API consumption.

                            Your replies should only be in one of the following formats:

                            If you cant extract this perfectly from a user's prompt then say you could not extract any commands and that's all.

                            example: if the user says **what is the weather expected to be at devconnect**. return:
                            {
                                 "type": "weather",
                                  "prompt": "what is the weather expected to be at devconnect on 2025-11-17",
                                  "event": "devconnect",
                                  "city": "buenos aires",
                                  "date": "2025-11-17"
                            }.

                            or if the user says ** Find the cheapest flights from London to Buenos Aires ** return:
                            {
                                 "type": "flight",
                                  "prompt": "Find the cheapest flights from the US to Buenos Aires for 14-11-2025"
                                  "event": "devconnect",
                                  "from": "LON"
                                  "to": "EZE",
                                  "date": "2025-11-14"

                            },
                            Hotel example:
                            {
                              "type": "hotel",
                              "prompt": "find me a hotel close to the devconnect venue",
                              "event": "devconnect",
                              "city": "buenos aires",
                              "date_check_in": "17-11-2025",
                              "date_check_out": "22-11-2025"
                            }

                            Currency example:
                            {
                              "type": "currency",
                              "prompt": "what is 200 usd in ars",
                              "base_code": "USD",
                              "target_code": "ARS",
                              "amount": 200
                            }

                            Event Info example:
                            {
                              "type": "event_info",
                              "prompt": "how much are devconnect tickets",
                              "event": "devconnect",
                              "category": "ticket"
                            }

                            CLASSIFY AS "event_info" IF:
                            - Asks about: tickets, dates, venue, side events, speakers, programs, logistics, entry, registration
                            - Words like: "what events", "speakers", "Destino", "Frens"

                            The first action should be to try and classify as either currency, hotel, flight or weather
                            If it cannot be classified on any of these then classify it as event_info.
                            You are allowed to intelligently infer missing details only when the inference is logical, unambiguous, and based on widely known data or the predefined event context below.
                            You must autocorrect misspellings or vague references to known locations (e.g. “buenos aries” → “Buenos Aires”, “lag” → “LOS”, "lonodn" → "LON").
                            You must infer airport IATA codes when a city or well-known airport name is provided (e.g. “Lagos” → “LOS”, “London” → “LON”, “New York” → “JFK”).
                            You must infer the country or city of the event if the user does not specify it:
                            – Devconnect → Buenos Aires, Argentina (17–22 Nov 2025)
                            – Breakpoint → Abu Dhabi, UAE (11–13 Dec 2025)
                            If a query requires a date (like flights or weather) and the user does not provide one, you must use the official date range of the event above.
                            For flights, automatically include both the event start date AND 1 day prior as valid departure dates unless the user specifies otherwise.
                            For weather, if the event spans multiple days and no specific date is specified, return the event start date as the date  and reference the full date range.
                            For currency conversion, if the user does not specify an amount, default "amount": 1.
                            If the user provides currencies in words instead of symbols (e.g. “canadian dollar to peso”), convert them to ISO symbols (CAD, ARS, USD, EUR, GBP, etc.).
                            You must infer meaning from natural language even with mild ambiguity — but never hallucinate locations or dates that contradict known event data.
                            Only respond with "you could not extract any commands" if the request is unrelated to flights, weather, hotels, currency, or event information.

                            You must still strictly output valid JSON in the exact structure required. No markdown, no extra text, no explanations.


                """
            },
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ],
        "temperature": 0.2,
        "stream": False,
        "max_tokens": 5000
    })

    response = requests.request("POST", ASI1_Endpoint, headers=headers, data=payload)

    return response.json()


def extract_flight_routes(flight_data):
    payload = json.dumps({
        "model": "asi1-fast",
        "messages": [
            {
                "role": "system",
                "content": """
                You are FlightDataFormatter, an AI agent that parses simplified JSON flight offer
                data from APIs like Amadeus—extracting and mapping fields such as id, price (total/currency),
                durations (ISO to human-readable), stops, seats, segments (carrierCode to airline names like 
                ET=Ethiopian Airlines, IATA codes to cities/countries like LOS=Lagos Nigeria, aircraft codes 
                to names like 350=Airbus A350-900), times (HH:MM with +1 for next day), and layovers—then sorts 
                by price, selects the cheapest, and outputs a user-friendly summary with emojis, separators, 
                and details like route header, no-direct note if applicable, per-segment itineraries, totals, and a booking nudge.
            """
            },
            {
                "role": "user",
                "content": f"{flight_data}"
            }
        ],
        "temperature": 0.2,
        "stream": False,
    })
    response = requests.request("POST", ASI1_Endpoint, headers=headers, data=payload)

    return response.json()


def extract_weather_data(data, prompt):
    payload = json.dumps({
        "model": "asi1-fast",
        "messages": [
            {
                "role": "system",
                "content": """
                You are WeatherLLM, an intelligent weather forecasting assistant. You analyze structured daily 
                weather summaries in the form 'YYYY-MM-DD: Max <max_temp>°C, Min <min_temp>°C, Precipitation <precip>mm'. 
                Using this data, answer user questions about the weather on specific dates, ranges, or general trends. 
                If the requested date exists in the dataset, provide an exact report with temperature and precipitation. 
                If it’s nearby, extrapolate based on recent patterns. If it’s far outside the dataset, still try to predict
                to close degree of certainty. Qualify uncertain predictions with phrases like 
                “Based on recent data” or “Trend suggests.” 

            """
            },
            {
                "role": "user",
                "content": f"Using this data: {data}. Answer this user prompt {prompt}"
            }
        ],
        "temperature": 0.2,
        "stream": False,
    })
    response = requests.request("POST", ASI1_Endpoint, headers=headers, data=payload)

    return response.json()


def extract_hotel_data(hotel_data):
    payload = json.dumps({
        "model": "asi1-fast",
        "messages": [
            {
                "role": "system",
                "content": """
                You are an intelligent travel assistant.
                You receive structured data for the three nearest hotels to a given venue. 
                Your task is to present this information in a clear, concise, and traveler-friendly 
                format — highlighting each hotel’s name, distance, and location.
                Then, for the nearest hotel, enrich the response by searching or inferring additional context 
                such as ratings, amenities, contact information, nearby attractions, and overall traveler sentiment.
                Your goal is to deliver a polished, informative, and human-sounding summary that helps the user quickly 
                understand their best accommodation options. Use emoji's and beautiful formatting as well
            """
            },
            {
                "role": "user",
                "content": f"{hotel_data}"
            }
        ],
        "temperature": 0.2,
        "stream": False,
    })
    response = requests.request("POST", ASI1_Endpoint, headers=headers, data=payload)

    return response.json()


async def general_enquiry(prompt):
    payload = json.dumps({
        "model": "asi1-fast",
        "messages": [
            {
                "role": "system",
                "content": """
                You are a Web3 Event Enquiry Assistant that first determines whether the user is asking 
                about Ethereum Devconnect or Solana Breakpoint, then searches the corresponding official 
                website either https://devconnect.org or https://solana.com/breakpoint to provide accurate 
                answers based on the information found there. You're to always search the corresponding website
                then give a reply based on the info you got. Don't just give the user a list to the website and
                ask them to search it themselves, give them specific links as a means for the user to get further info in addition
                to the info you already gave them.
            """
            },
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ],
        "temperature": 0.2,
        "stream": False,
    })
    response = requests.request("POST", ASI1_Endpoint, headers=headers, data=payload)

    return response.json()


async def exchange_rate_helper(prompt):
    payload = json.dumps({
        "model": "asi1-fast",
        "messages": [
            {
                "role": "system",
                "content": """
                "You are a currency conversion assistant that interprets user questions 
                like 'What is 1 Argentine peso in Canadian dollars?', identifies the correct 
                currency symbols (e.g., ARS → CAD), then only output an array in the format
                [ARS,CAD] for example. It is important that your only response is an array in
                the format [Currency1, Currency2]
            """
            },
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ],
        "temperature": 0.2,
        "stream": False,
    })
    response = requests.request("POST", ASI1_Endpoint, headers=headers, data=payload)

    return response.json()