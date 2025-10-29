"""
The `get_currencies` function uses an asynchronous helper (`exchange_rate_helper`) to extract two
currency codes from a user prompt, then cleans and returns them. The `fetch_exchange_rates` function
retrieves live exchange rate data from the ExchangeRate API, calculates the conversion for a given
amount, and returns a formatted message showing the current rate and timestamp.
"""

import requests
from helpers import exchange_rate_helper
import asyncio
from uagents import Model, Field

class CurrencyConversionRequest(Model):
    base_code: str
    other_currency: str

class CurrencyConversionResponse(Model):
    results: str

def get_currencies(prompt):

    output = asyncio.run(exchange_rate_helper(prompt))
    currencies = output["choices"][0]["message"]["content"]

    # currencies = "[GBP,ARS]"

    currencies = currencies.strip("[]").split(",")
    currencies = [c.strip() for c in currencies]

    base_code = currencies[0]
    other_currency = currencies[1]

    print(base_code, other_currency)
    return base_code, other_currency



def fetch_exchange_rates(base_code, target_code, amount):
    url = 'https://v6.exchangerate-api.com/v6/f10aad56bb1665e3114dd115/latest/'+base_code

    # Making our request
    response = requests.get(url)
    data = response.json()

    last_update = data["time_last_update_utc"]
    rate = data["conversion_rates"][str(target_code)]
    if amount == 1:
        return f"As of {last_update}, 1 ${base_code} = {rate} ${target_code}."
    else:
        return f"As of {last_update}, {amount} {base_code} = {rate * amount:.6f} {target_code}."

