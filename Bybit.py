import json
import httpx
import requests
import time
import hmac
import hashlib
from .Errors import ExchangeError
from .Config import config

"""
Нужно сделат единую функицю запросов. Не совсем понятно что делать с payload
"""
class Bybit:
    def __init__(self) -> None:
        self.api_key = ''
        self.secret_key = ''
        self.settings = {}
        self.commision = 0.1
        # Keys: 'networks': {'coin': {'networkName': {'eW': True/False, 'eD': True/False}}} - сети для определенной монеты биржи
        #       'symbols': {'symbol': {'b': baseAsset, 'q': quoteAsset'}} - Base и Quote assets символа
        #       'pairs': [symbols] - все торговые пары
        #       'data': {symbol: {'ask': ask, 'bid': bid} - данные символов ask, bid и объем
        #       'pairsMargin': [symbolsIsMargin] - все символы, котореы поддерживают маржинальную торговалю (для арбитража с хэджированием) (118)

    async def loadNetworks(self) -> None:
        """
        Асинхронная загрзука сетей вывода и депозита для монет
        """
        recv_window = str(5000)
        timestamp = str(int(time.time() * 1000))
        def genSignature():
            payload = ''
            paramStr = str(timestamp) + self.api_key + recv_window + payload
            hash = hmac.new(bytes(self.secret_key, "utf-8"), paramStr.encode("utf-8"), hashlib.sha256)
            signature = hash.hexdigest()
            return signature
        headers = {
            'X-BAPI-SIGN': genSignature(),
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window
        }
        async with httpx.AsyncClient() as client:
            responce = await client.get('https://api.bybit.com/v5/asset/coin/query-info', headers=headers)
            data = responce.json()
            networksKeyAdd = {}
            if responce.status_code == 200:
                try:
                    for coin in data['result']['rows']:
                        coinAdd = coin['coin']
                        networksAdd = {}
                        for networks in coin['chains']:
                            networkName = networks['chain']
                            flagW = False
                            flagD = False
                            if networks['chainDeposit'] == '1':
                                flagD = True
                            if networks['chainWithdraw'] == '1':
                                flagW = True
                            
                            networkData = {
                                'eW': flagW,
                                'eD': flagD,
                                'fee': networks['withdrawFee'],
                                'min': networks['withdrawMin']
                            }

                            networksAdd[networkName] = networkData
                        networksKeyAdd[coinAdd] = networksAdd
                    self.settings['networks'] = networksKeyAdd
                except KeyError as e:
                    raise ExchangeError("Bybit", responce.text)

    async def loadSymbols(self) -> None:
        """
        Асинхронная загрузка настроек Base и Quote assets символов. 
        b - Base Asset, q - Quote Asset, p - precision для торговли на биржи(окргуление)
        Асинхронная загрзука всех пар с биржи
        """
        settings = {}
        pairs = []
        pairsMargin = []
        async with httpx.AsyncClient() as client:
            responce = await client.get('https://api.bybit.com/v5/market/instruments-info?category=spot')
            data = responce.json()
            for symbol in data['result']['list']:
                if symbol['marginTrading'] != 'none':
                    pairsMargin.append(symbol['symbol'])
                settings[symbol['symbol']] = {'b': symbol['baseCoin'], 'q': symbol['quoteCoin'], 'p': symbol['lotSizeFilter']['basePrecision']}
                pairs.append(symbol['baseCoin'] + '/' + symbol['quoteCoin'])
            self.settings['symbols'] = settings
            self.settings['pairs'] = pairs
            self.settings['pairsMargin'] = pairsMargin

    def requestGET(self, endpoint, method, asyn = None):

        def genGepositAddres(coin):
            recv_window = str(5000)
            timestamp_utc = str(int(time.time() * 1000))
            def genSignature():
                payload = f'coin={coin}'
                param_str = str(timestamp_utc) + self.api_key + recv_window + payload
                hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
                signature = hash.hexdigest()
                return signature
            headers = {
                'X-BAPI-SIGN': genSignature(),
                'X-BAPI-API-KEY': self.api_key,
                'X-BAPI-TIMESTAMP': timestamp_utc,
                'X-BAPI-RECV-WINDOW': str(5000)
            }
            responce = requests.get(f'https://api.bybit.com/v5/asset/deposit/query-address?coin={coin}', headers=headers)
            
            if responce.status_code == 200:
                return responce.json()
            else:
                raise ExchangeError("bybit", responce)
            
    def isActive(self) -> bool:
        if config['Bybit'] == True:
            return True
        else:
            return False
    
    def getName(self):
        return 'Bybit'

    def getSToSymbol(self, symbol) -> str:
        symbolAdd = self.settings['symbols'][symbol]
        data  = f'https://www.bybit.com/ru-RU/trade/spot/{symbolAdd["b"] + "/" + symbolAdd["q"]}'
        return data
    
    async def create_margin_order(self, symbol, side, amount, price):
        recv_window = str(5000)
        timestamp = str(int(time.time() * 1000))

        payload = {
            "category": "spot",
            "symbol": symbol,
            "side": side, # Buy / Sell
            "orderType": "Limit",
            "qty": amount,
            "price": price,
            "isLeverage": 1,
        }

        def genSignature(payload):
            payloadAdd = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
            paramStr = str(timestamp) + self.api_key + recv_window + payloadAdd
            hash = hmac.new(bytes(self.secret_key, "utf-8"), paramStr.encode("utf-8"), hashlib.sha256)
            signature = hash.hexdigest()
            return signature
        
        headers = {
            'X-BAPI-SIGN': genSignature(payload),
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window
        }
        async with httpx.AsyncClient() as client:
            responce = await client.get('https://api.bybit.com/v5/order/create', headers=headers)
            if responce.status_code == 200:
                return responce.json()
            else:
                return 'error'
    
    async def createOrder(self, symbol, side, amount, price, typeOrder = None):
        recv_window = str(5000)
        timestamp = str(int(time.time() * 1000))

        sideSymbol = None
        if side.upper() == 'BUY':
            sideSymbol = 'Buy'
        if side.upper() == 'SELL':
            sideSymbol = 'Sell'

        payload = {
            "category": "spot",
            "symbol": symbol,
            "side": sideSymbol,
            "orderType": "Limit",
            "qty": str(amount),
            "price": str(price),
        }

        def genSignature(payload):
            payloadAdd = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
            paramStr = str(timestamp) + self.api_key + recv_window + payloadAdd
            hash = hmac.new(bytes(self.secret_key, "utf-8"), paramStr.encode("utf-8"), hashlib.sha256)
            signature = hash.hexdigest()
            return signature
        
        headers = {
            'X-BAPI-SIGN': genSignature(payload),
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window
        }
        async with httpx.AsyncClient() as client:
            responce = await client.get('https://api.bybit.com/v5/order/create', headers=headers)
            if responce.status_code == 200:
                return responce.json()
            else:
                return 'error'
            
    
