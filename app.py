from unittest import result
import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, render_template
from collections import ChainMap

NBP_API_EX_RATES_URL = 'http://api.nbp.pl/api/exchangerates/tables/A/'
CINKCIARZ_SCRAPING_RATE_URL = 'https://cinkciarz.pl/wa/pe/transactional?subscriptionId=PLN&unit=50000'

app = Flask(__name__)


def check_is_currency(currency, nbp_ex):
    if currency in nbp_ex:
        return True
    else:
        return False


def comparison(cin_ex, nbp_ex, all_currency):
    result = []
    for currency in all_currency:
        if check_is_currency(currency, cin_ex):
            if check_is_currency(currency, nbp_ex):
                if (float(nbp_ex[currency]) <= float(cin_ex[currency],)):
                    result.append(
                        f'Lepszy przelicznik  {currency}  jest na NBP : {nbp_ex[currency]}')
                else:
                    result.append(
                        f'Lepszy przelicznik  {currency}  jest na Cinkciarzu : {cin_ex[currency]}')
            else:
                result.append(
                    f'Nie ma waluty na NBP przelicznik z Cinkciarza:  {cin_ex[currency]}')
        else:
            result.append(
                f'Nie ma waluty na Cinkciarzu przelicznik z NBP:  {nbp_ex[currency]}')
    return result


def sum_currency(cin_ex, nbp_ex):
    return list(ChainMap(cin_ex, nbp_ex))


ex_rates, *_ = requests.get(NBP_API_EX_RATES_URL).json()
cin_ex_rates = requests.get(CINKCIARZ_SCRAPING_RATE_URL)


nbp_ex_rates = {}
for rate in ex_rates['rates']:
    nbp_ex_rates[rate['code']] = rate['mid']


soup = BeautifulSoup(cin_ex_rates.text, "lxml")
table = soup.find("table", attrs={"class": "table"})
table_data = table.tbody.find_all("tr")

headings = []
cin_ex_rate = {}
for index in range(len(table_data)):
    currency = []
    for td in table_data[index].find_all("td"):
        currency.append(td.text.replace('\n', ' ').strip())
    cin_ex_rate[currency[2]] = currency[4]
    headings.append(currency)

new_cin_ex_rates = {}
for rate in cin_ex_rate:
    new_cin_ex_rates[(rate.split().pop())] = cin_ex_rate[rate].replace(',', '.')


all_currency = sum_currency(new_cin_ex_rates, nbp_ex_rates)


@app.route('/')
def my_form():
    return render_template('testy.html', wyniki=comparison(new_cin_ex_rates, nbp_ex_rates, all_currency))


if __name__ == '__main__':
    app.run(debug=True)
