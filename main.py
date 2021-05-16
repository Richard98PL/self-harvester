from binance.client import Client,AsyncClient
import asyncio
import json
import sys
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from help import *

# configuration section
TRADING_WEEKLY_FLUCTUATION_THRESHOLD = 12
TRADING_CURRENCY = BTC
# EOF configuration section

BINANCE_API_KEY = 'binance_api_key'
BINANCE_API_SECRET = 'binance_api_secret'

async def main():

    initLog()
    keys_json = getKeys()

    client = await AsyncClient.create(keys_json[BINANCE_API_KEY], 
                                      keys_json[BINANCE_API_SECRET])

    # if checkIfCurrencyFromPreviousTransactionHasChanged(TRADING_CURRENCY):
        # await sellMarket(previousTransactionCurrencyJSON(),client)

    CURRENCY_BALANCE = await getAssetBalance(TRADING_CURRENCY['symbol'],client)
    USDT_BALANCE = await getAssetBalance('USDT',client)

    canYouBuy = False
    canYouSell = False

    if float(USDT_BALANCE['free']) > 1 :
        print('You have ' + USDT_BALANCE['free'] + ' dollars')
        canYouBuy = True
    else:
        print('You have ' + CURRENCY_BALANCE['free'] + ' ' + CURRENCY_BALANCE['asset'])
        canYouSell = True

    shouldYouBuy = coinmarketcapLogic(TRADING_WEEKLY_FLUCTUATION_THRESHOLD,TRADING_CURRENCY)

    if shouldYouBuy:
        if canYouBuy:
            await buyMarket(TRADING_CURRENCY,client)
        else:
            print('Assets already bought. HODL!')
    else:
        if canYouSell:
            await sellMarket(TRADING_CURRENCY,client)
        else:
            print('You have nothing to sell! Wait to buy!')

    await client.close_connection()

if __name__ == "__main__":

    print('Execution begins.\n')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print('\nExecution completed succesfully.')