import asyncio
import requests
import json
from pprint import pprint

async def main():
  #Debug
  print("container started")

  #Get the date of today in format yyyy-mm-dd
  from datetime import date, datetime, timedelta
  today = date.today()
  today = today.strftime("%Y-%m-%d")
  tomorrow = date.today() + timedelta(days=1)
  # if time is past noon, get the prices for the next day
  if datetime.now().hour >= 12:
      pollDate = tomorrow
  else:
      pollDate = today

  url = "https://graphql.frankenergie.nl/"

  payload = json.dumps({
    "query": f"""
    query MarketPrices {{
      marketPrices(date: "{pollDate}") {{
        electricityPrices {{
          from
          till
          marketPrice
          marketPriceTax
          sourcingMarkupPrice
          energyTaxPrice
          perUnit
        }}
        gasPrices {{
          from
          till
          marketPrice
          marketPriceTax
          sourcingMarkupPrice
          energyTaxPrice
          perUnit
        }}
      }}
    }}
    """
  })
  headers = {
    'x-country': 'BE',
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  #Check the response health
  if response.status_code != 200:
      print(f"Error: {response.status_code}")
      exit()

  #Get the electricity prices
  try:
      electricityPrices = json.loads(response.text)['data']['marketPrices']['electricityPrices']
  except KeyError:
      print("Error: No electricity prices found")
      exit()

  #Create an 2 dimensional array of the hour and the market prices of electricity in MWh round to two decimals
  electricityPricesList = list()
  for i in range(len(electricityPrices)):
      electricityPricesList.append([electricityPrices[i]['from'], round(electricityPrices[i]['marketPrice']*1000, 2)])

  pprint(electricityPricesList)

  from plcnext import run_plc_operations

  if __name__ == "__main__":
      await run_plc_operations(electricityPricesList)


if __name__ == "__main__":
    asyncio.run(main())