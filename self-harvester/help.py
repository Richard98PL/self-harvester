from binance.client import Client,AsyncClient
import asyncio
import json
import math
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os
from datetime import datetime

from keys import *

interestingCurrencies = ['BTC','ETH','BNB','ADA','DOGE','XRP','DOT','LTC','SHIB','NEO']

BTC = {'symbol': 'BTC', 'precision': 6}
DOGE = {'symbol' : 'DOGE', 'precision' : 1}
ETH = {'symbol' :'ETH', 'precision' : 2}
BNB = {'symbol' :'BNB', 'precision' : 3}


def round_decimals_down(number:float, decimals:int=2):
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor

def jsonPrint(text):
    print(json.dumps(text,indent=4,sort_keys=4))
    
async def printCurrenyInfo(symbol_text,client):
    jsonPrint(await client.get_symbol_ticker(symbol=symbol_text))

async def getCurrencyValue(symbol_text,client):
    currencyInfo = await client.get_symbol_ticker(symbol=symbol_text + 'USDT')
    return currencyInfo

async def printCurrenyValue(symbol_text,client):
    jsonPrint(await client.get_symbol_ticker(symbol=symbol_text + 'USDT'))

async def printInterestingCurrenciesValues(client):
    for currency in interestingCurrencies:
        jsonPrint(await client.get_symbol_ticker(symbol=currency + 'USDT'))

async def printOrders(client):
    jsonPrint(await client.get_open_orders())

orderValues = ['price','type','origQty']
async def printOrdersValues(client):
    for jsonObject in await client.get_open_orders():
        for value in orderValues:
            print(value + ": " + jsonObject[value])
        print("price*origQty: USD  " + str(round(float(jsonObject['price']) * float(jsonObject['origQty']),2)))

async def cancelAllOrders(client):
    for openOrder in await client.get_open_orders():
        await client.cancel_order(
            symbol = openOrder['symbol'],
            orderId = openOrder['orderId']
        )

async def getAssetBalance(currency,client):
    balance = await client.get_asset_balance(asset=currency)
    return balance

async def sellMarket(assetDict,client):
    assetInfo = await getAssetBalance(assetDict['symbol'],client)
    assetSymbol = assetInfo['asset']
    assetFreeQuantity = assetInfo['free']
    if  round_decimals_down(float(assetFreeQuantity),assetDict['precision']) > 0:
        print('selling ' + assetSymbol + ' with quantity of ' + str(round_decimals_down(float(assetFreeQuantity),assetDict['precision'])))
        await client.order_market_sell(
            symbol = assetSymbol + 'USDT',
            quantity = round_decimals_down(float(assetFreeQuantity),assetDict['precision'])
        )
        print('Your sale was successful ')
        assetDict['function'] = 'sellMarket'
        assetDict['datetime'] = datetime.now()
        assetDict['sold'] = assetInfo
        assetDict['profit'] = await getAssetBalance('USDT',client)
        with open(os.path.join(getCurrentLocation(),'logs.json'), 'a', encoding='utf-8') as f:
                json.dump(assetDict, f, ensure_ascii=False, indent=4,default=str)
                f.write(",\n")
    
    else:
        print('Asset is 0.')

async def buyMarket(assetDict,client):
    currencyInfo = await getCurrencyValue(assetDict['symbol'],client)
    assetInfo = await getAssetBalance('USDT',client)
    howManyAssetCanIBuyWithCurrentBalance = round_decimals_down(( 0.99 * float(assetInfo['free']) / float(currencyInfo['price']) ),assetDict['precision'])
    print('howManyAssetCanIBuyWithCurrentBalance = ' + str(howManyAssetCanIBuyWithCurrentBalance))
    await client.order_market_buy(
        symbol = assetDict['symbol'] + 'USDT',
        quantity = howManyAssetCanIBuyWithCurrentBalance
    )

    with open(os.path.join(getCurrentLocation(),'previousTransactionSymbol.json'), 'w', encoding='utf-8') as f:
            json.dump(assetDict, f, ensure_ascii=False, indent=4)
    
    assetDict['function'] = 'buyMarket'
    assetDict['datetime'] = datetime.now()
    assetDict['spend'] = assetInfo
    assetDict['bought'] = str(howManyAssetCanIBuyWithCurrentBalance) + assetDict['symbol']
    with open(os.path.join(getCurrentLocation(),'logs.json'), 'a', encoding='utf-8') as f:
            json.dump(assetDict, f, ensure_ascii=False, indent=4,default=str)
            f.write(",\n")

    print('Your purchase was successful.')

def getCurrentLocation():
    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def coinmarketcapUtility():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start':'1',
        'limit':'5000',
        'convert':'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': coinmarketcap_key
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)

        __location__ = getCurrentLocation()

        with open(os.path.join(__location__,'coinmarketcapinfo.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        values = []
        temporaryJson = {}
        for jsonObject in data['data']:
            if jsonObject['symbol'] in interestingCurrencies:
                temporaryJson['symbol'] = jsonObject['symbol']
                temporaryJson['24h'] = jsonObject['quote']['USD']['percent_change_24h']
                temporaryJson['7d'] = jsonObject['quote']['USD']['percent_change_7d']
                values.append(temporaryJson)
                temporaryJson = {}
        
        with open(os.path.join(__location__,'fluctuations.json'), 'w', encoding='utf-8') as f:
            json.dump(values, f, ensure_ascii=False, indent=4)

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def sortFunction(value):
	return value["7d"]

def coinmarketcapLogic(TRADING_WEEKLY_FLUCTUATION_THRESHOLD,TRADING_CURRENCY):
    print('TRADING_WEEKLY_FLUCTUATION_THRESHOLD = ' + str(TRADING_WEEKLY_FLUCTUATION_THRESHOLD))
    coinmarketcapUtility()
    with open(os.path.join(getCurrentLocation(),'fluctuations.json')) as data_file:    
        data = json.load(data_file)
        data = sorted(data, key=sortFunction)
        shouldYouBuy = False
        for currency in data:
            if currency['symbol'] == TRADING_CURRENCY['symbol'] and currency['7d'] < - TRADING_WEEKLY_FLUCTUATION_THRESHOLD:
                print(TRADING_CURRENCY['symbol'] + ' fluctuation is less than -' + str(TRADING_WEEKLY_FLUCTUATION_THRESHOLD) + '%. [' + str(currency['7d']) + ']')
                shouldYouBuy = True
            elif currency['symbol'] == TRADING_CURRENCY['symbol'] and currency['7d'] > TRADING_WEEKLY_FLUCTUATION_THRESHOLD:
                 print(TRADING_CURRENCY['symbol'] + ' fluctuation is more than ' + str(TRADING_WEEKLY_FLUCTUATION_THRESHOLD) + '%. [' + str(currency['7d']) + ']')

    return shouldYouBuy
    
def checkIfCurrencyFromPreviousTransactionHasChanged(TRADING_CURRENCY):
     with open(os.path.join(getCurrentLocation(),'previousTransactionSymbol.json')) as data_file:    
        data = json.load(data_file)
        print('previousTransactionSymbol ' + str(data['symbol']))
        print('currentTransactionSymbol ' + str(TRADING_CURRENCY['symbol']))
        return (data['symbol'] != TRADING_CURRENCY['symbol'])

def previousTransactionCurrencyJSON():
    with open(os.path.join(getCurrentLocation(),'previousTransactionSymbol.json')) as data_file:  
        return json.load(data_file)

def initLog():
    log = {'datetime' : datetime.now(), 'function' : 'init'}
    with open(os.path.join(getCurrentLocation(),'logs.json'), 'a', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=4,default=str)
            f.write(",\n")