import requests
import time
from .Errors import ExchangeError
import hmac
import hashlib
from .Config import config
import httpx
import asyncio
import datetime
import base64

class Okx:
    def __init__(self) -> None:
        self.apiKey = ''
        self.apiSecret = ''
        self.settings = {}
        self.commision = 0.1
        # Keys: 'networks': {'coin': {networks}} - сети для определенной монеты биржи
        #       'symbols': {'symbol': {'b': baseAsset, 'q': quoteAsset'}} - Base и Quote assets символа
        #       'pairs': [symbols] - все торговые пары
        #       'data': {symbol: {'ask': ask, 'bid': bid} - данные символов ask, bid и объем
        #       'pairsMargin': [symbolsIsMargin] - все символы, котореы поддерживают маржинальную торговалю (для арбитража с хэджированием) (вроде не поддерживает)
    
    async def asyncGET(self, endpoint, method, params = None, addres = None):
        """
        Асинхронный запрос
        """
        url = 'https://www.okx.com' + endpoint
        if method == 'public':
            async with httpx.AsyncClient() as client:
                responce = await client.get(url)

                if responce.status_code == 200:
                    return responce.json()
                else:
                    print(responce.status_code)
                    raise ExchangeError('OKX', responce.text)
                
        timestamp = self.getTimestamp()
        def signature(request_path, body):
            if str(body) == '{}' or str(body) == 'None':
                body = ''
            message = str(timestamp) + str.upper('GET') + request_path + str(body)
            mac = hmac.new(bytes(self.apiSecret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
            d = mac.digest()
            return base64.b64encode(d)
        
        if method == 'private': 
            async with httpx.AsyncClient() as client:
                headers = {
                    'OK-ACCESS-KEY': config['api_keys']['okx']['api_key'],
                    'OK-ACCESS-SIGN': signature(),
                    'OK-ACCESS-TIMESTAMP': timestamp,
                    'OK-ACCESS-PASSPHRASE': config['api_keys']['okx']['password'],
                    'Content-Type': 'application/json'
                }
                responce = await client.get(url)

    async def loadNetworks(self) -> None:
        """
        Асинхронная загрузка сетей для вывода и депозита монет
        """
        timestamp = self.getTimestamp()
        def genSignature(request_path, body):
            if str(body) == '{}' or str(body) == 'None':
                body = ''
            message = str(timestamp) + 'GET' + request_path + str(body)
            mac = hmac.new(bytes(self.apiSecret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
            d = mac.digest()
            return base64.b64encode(d)
        sign = genSignature('/api/v5/asset/currencies', {})
        headers = {
            'OK-ACCESS-KEY': self.apiKey,
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': "CODDICODDICODi1!",
            'Content-Type': 'application/json'
        }
        async with httpx.AsyncClient() as client:
            responce = await client.get('https://www.okx.com/api/v5/asset/currencies', headers=headers)
            data = responce.json()

            networksKeyAdd = {}
            for coin in data['data']:
                networksAdd = {}
                coinAdd = coin['ccy']
                network = coin['chain'].split('-')[1]

                networkAddData = {
                    'eW': coin['canWd'],
                    'eD': coin['canDep'],
                    'fee': coin['minFee'],
                    'min': coin['minWd']
                }
                try:
                    key = networksKeyAdd[coinAdd]
                    networksCoin = networksKeyAdd[coinAdd]
                    networksCoin[network] = networkAddData
                    networksKeyAdd[coinAdd] = networksCoin
                except KeyError:
                    networksAdd[network] = networkAddData
                    networksKeyAdd[coinAdd] = networksAdd
            self.settings['networks'] = networksKeyAdd 

    async def loadSymbols(self) -> None:
        """
        Асинхронная загрузка символов, Base и Quote assets.
        Асинхронная загрузка всех пар биржи.
        """
        symbols = {}
        pairs = []
        data = await self.asyncGET('/api/v5/public/instruments?instType=SPOT', 'public')
        for symbol in data['data']:
            symbolSplit = symbol['instId'].split('-')
            symbolAdd = symbolSplit[0] + symbolSplit[1]
            symbols[symbolAdd] = {'b': symbol['baseCcy'], 'q': symbol['quoteCcy']}
            pairs.append(symbol['baseCcy'] + '/' + symbol['quoteCcy'])
        self.settings['symbols'] = symbols
        self.settings['pairs'] = pairs
        self.settings['pairsMargin'] = []

    async def loadData(self) -> None:
        """
        Асинхронная загрзука данных для символов. Bid и Ask цен
        """
        
    def isActive(self) -> bool:
        if config['Okx'] == True:
            return True
        else:
            return False
    
    def getName(self):
        return 'Okx'
    

    def getTimestamp(self) -> int:
        now = datetime.datetime.utcnow()
        t = now.isoformat("T", "milliseconds")
        return t + "Z"
    
    def getSToSymbol(self, symbol) -> str:
        symbolAdd = self.settings['symbols'][symbol]
        data  = f'https://www.okx.com/ru/trade-spot/{symbolAdd["b"].lower() + "-" + symbolAdd["q"].lower()}'
        return data