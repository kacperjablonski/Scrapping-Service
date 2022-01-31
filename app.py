from unittest import result
import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, render_template


app = Flask(__name__)


NBP_API_GOLD_PRICE_URL = 'http://api.nbp.pl/api/cenyzlota'
NBP_API_EX_RATES_URL = 'http://api.nbp.pl/api/exchangerates/tables/A/'
CINKCIARZ_SCRAPING_RATE_URL = 'https://cinkciarz.pl/wa/pe/transactional?subscriptionId=PLN&unit=50000'

# function compere Value and add to the list


def compperre(cin_ex, nbp_ex, all_currency):
    result = []
    for key in all_currency:
        if key in nbp_ex and key in cin_ex:
            if (float(nbp_ex[key]) <= float(cin_ex[key])):
                result.append(
                    f'Lepszy przelicznik  {key}  jest na NBP : {nbp_ex[key]}')
            elif (float(nbp_ex[key]) > float(cin_ex[key])):
                result.append(
                    f'Lepszy przelicznik  {key}  jest na Cinkciarzu : {cin_ex[key]}')
        elif key in nbp_ex:
            result.append(f'Waluta {key} tylko na NBP po  {nbp_ex[key]}')
        elif key in cin_ex:
            result.append(
                f'Waluta {key} tylko na Cinkciarzu po  {cin_ex[key]}')
    return result

# function sum all currency


def sum_dict(cin_ex, nbp_ex):
    my_list = []
    for key in cin_ex:
        my_list.append(key)
    for key in nbp_ex:
        my_list.append(key)
    return list(set(my_list))


gold_price = requests.get(NBP_API_GOLD_PRICE_URL).json().pop()
ex_rates = requests.get(NBP_API_EX_RATES_URL).json().pop()
cin_ex_rates = requests.get(CINKCIARZ_SCRAPING_RATE_URL)


nbp_ex_rates = {}
for rate in ex_rates['rates']:
    nbp_ex_rates[rate['code']] = rate['mid']


soup = BeautifulSoup(cin_ex_rates.text, "lxml")
table = soup.find("table", attrs={"class": "table"})
table_data = table.tbody.find_all("tr")

# Get all the headings of Lists
headings = []
cin_ex_rate = {}
for index in range(len(table_data)):
    currency = []
    for td in table_data[index].find_all("td"):
        currency.append(td.text.replace('\n', ' ').strip())
    cin_ex_rate[currency[2]] = currency[4]
    headings.append(currency)

new_cin_ex_rates = {}
for i in cin_ex_rate:
    new_cin_ex_rates[(i.split().pop())] = cin_ex_rate[i].replace(',', '.')


all_currency = sum_dict(new_cin_ex_rates, nbp_ex_rates)


@app.route('/')
def my_form():
    return render_template('testy.html', wyniki=compperre(new_cin_ex_rates, nbp_ex_rates, all_currency))


if __name__ == '__main__':
    app.run(debug=True)
