import requests
import time
from .Errors import ExchangeError
import hmac
import hashlib
from .Config import config
import httpx
import asyncio


class Kucoin:
    def __init__(self) -> None:
        self.apiKey = ''
        self.apiSecret = ''
        self.notSymbols = ['KCS', 'MC', 'BIFI']
        self.settings = {}
        self.commision = 0.1
        # Keys: 'networks': {'coin': {networks}} - сети для определенной монеты биржи
        #       'symbols': {'symbol': {'b': baseAsset, 'q': quoteAsset'}} - Base и Quote assets символа
        #       'pairs': [symbols] - все торговые пары
        #       'data': {symbol: {'ask': ask, 'bid': bid} - данные символов ask, bid и объем
        #       'pairsMargin': [symbolsIsMargin] - все символы, котореы поддерживают маржинальную торговалю (для арбитража с хэджированием) (193)
    
    async def asyncGET(self, endpoint, method):
        """
        Асинхронный запрос
        """
        url = 'https://api.kucoin.com' + endpoint
        if method == 'public':
            async with httpx.AsyncClient() as client:
                responce = await client.get(url)

                if responce.status_code == 200:
                    return responce.json()
                else:
                    raise ExchangeError('Kucoin', responce.text)
                
        elif method == 'private': 
            async with httpx.AsyncClient() as client:
                responce = await client.get(url)

                if responce.status_code == 200:
                    return responce.json()
                else:
                    raise ExchangeError('Kucoin', responce.text)
        else:
            return 'method error'

    async def loadNetworks(self) -> None:
        """
        Асинхронная загрузка сетей для вывода и депозита монет
        """
        dataAdd = {}
        data = await self.asyncGET('/api/v3/currencies', 'public')
        for symbol in data['data']:
            networkDataAdd = {}
            if symbol['chains'] != None:
                for network in symbol['chains']:
                    networkDict = {
                        'eW': network['isWithdrawEnabled'],
                        'eD': network['isDepositEnabled'],
                        'fee': network['withdrawalMinFee'],
                        'min': network['withdrawalMinSize']
                    }
                    networkDataAdd[network['chainName']] = networkDict
                dataAdd[symbol['currency']] = networkDataAdd
            else:
                continue
        self.settings['networks'] = dataAdd


    async def loadSymbols(self) -> None:
        """
        Асинхронная загрузка символов, Base и Quote assets.
        Асинхронная загрузка всех пар биржи.
        """
        symbols = {}
        pairs = []
        pairsMargin = []
        data = await self.asyncGET('/api/v2/symbols', 'public')
        for symbol in data['data']:
            symbolAdd = symbol['baseCurrency'] + symbol['quoteCurrency']

            if symbol['baseCurrency'] not in self.notSymbols:
                if symbol['isMarginEnabled']:
                    pairsMargin.append(symbolAdd)
                symbols[symbolAdd] = {'b': symbol['baseCurrency'], 'q': symbol['quoteCurrency']}
                pairs.append(symbol['baseCurrency'] + '/' + symbol['quoteCurrency'])
        self.settings['symbols'] = symbols
        self.settings['pairs'] = pairs
        self.settings['pairsMargin'] = pairsMargin

    def getName(self):
        return 'Kucoin'
    
    def isActive(self) -> bool:
        if config['Kucoin'] == True:
            return True
        else:
            return False
        
    def getSToSymbol(self, symbol) -> str:
        symbolAdd = self.settings['symbols'][symbol]
        data = f'https://www.kucoin.com/ru/trade/{symbolAdd["b"] + "-" + symbolAdd["q"]}'
        return data
        
    async def createOrder(self, symbol, side, amount, price, typeOrder = None):
        try:
            data = await self.asyncGET('/api/v1/orders', 'public')
        except ExchangeError:
            pass
