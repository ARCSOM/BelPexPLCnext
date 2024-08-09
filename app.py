import requests
import json
from pprint import pprint

#Debug
print("container started")

#Get the date of today in format yyyy-mm-dd
from datetime import date
today = date.today()
today = today.strftime("%Y-%m-%d")


url = "https://graphql.frankenergie.nl/"

payload = json.dumps({
  "query": f"""
  query MarketPrices {{
    marketPrices(date: "{today}") {{
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
electricityPricesArray = []
for i in range(len(electricityPrices)):
    electricityPricesArray.append([electricityPrices[i]['from'], round(electricityPrices[i]['marketPrice']*1000, 2)])

pprint(electricityPricesArray)

