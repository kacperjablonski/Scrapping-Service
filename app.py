from unittest import result
import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, render_template
from collections import ChainMap

NBP_API_EX_RATES_URL = 'http://api.nbp.pl/api/exchangerates/tables/A/'
CINKCIARZ_SCRAPING_RATE_URL = 'https://cinkciarz.pl/wa/pe/transactional?subscriptionId=PLN&unit=50000'

ex_rates_raw, *_ = requests.get(NBP_API_EX_RATES_URL).json()
cin_ex_rates_raw = requests.get(CINKCIARZ_SCRAPING_RATE_URL).text

app = Flask(__name__)
def printing_one (market , currency, prise):
    print (f' Lepszy przelicznik jest {currency} na {market} po {prise}'  )

def printing_two(market ,currency, prise) :   
    print (f' {currency} jest tylko na {market} po {prise}'  )

def check_market(currency, market_cin, market_nbp):
    if currency in market_cin and currency in market_nbp:
        return True
    else : 
        return 'Cinkciarz' if currency in market_cin else 'NBP '
 
 
def comparison(cin_ex, nbp_ex, all_currency):
    
    
    for currency in all_currency:
        try:
            market=  'Cinkciarz' if cin_ex[currency] > nbp_ex[currency] else 'NBP'
            printing_one(market, currency , cin_ex[currency] if cin_ex[currency] > nbp_ex[currency] else nbp_ex[currency] )    
        except:
            market = check_market(currency, cin_ex, nbp_ex)
            printing_two(market , currency , cin_ex[currency] if market == 'Cinkciarz' else nbp_ex[currency] )


def sum_currency(cin_ex, nbp_ex):
    return list(ChainMap(cin_ex, nbp_ex))



exchange_rates_nbp, nbp_ex_rates_date = ex_rates_raw['rates'], ex_rates_raw['effectiveDate']

nbp_ex_rates = {}
for currency_index in exchange_rates_nbp:
    nbp_ex_rates[currency_index['code']] = currency_index['mid']


parse_cin_ex_rates = BeautifulSoup(cin_ex_rates_raw, "lxml")
get_table_cin_ex_rates = parse_cin_ex_rates.find(
    "table", attrs={"class": "table"})
table_data = get_table_cin_ex_rates.tbody.find_all("tr")



cin_ex_rate = {}
for td in table_data:
    clean_td = td.text.replace('\n', ' ').strip() 
    currency , price , *_ = clean_td.strip().split()[-3:]
    cin_ex_rate[currency] = float(price.replace(',',"."))


print(cin_ex_rate)


all_currency = sum_currency(cin_ex_rate, nbp_ex_rates)
comparison(cin_ex_rate, nbp_ex_rates, all_currency)

# @app.route('/')
# def my_form():
#     return render_template('testy.html', wyniki=comparison(cin_ex_rate, nbp_ex_rates, all_currency))


# if __name__ == '__main__':
#     app.run(debug=True)
