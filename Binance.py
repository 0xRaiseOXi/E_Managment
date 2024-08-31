import time
from .Errors import BinanceError, ExchangeError
import hmac
import hashlib
from .Config import config
import httpx

class Binance:
    def __init__(self) -> None:
        self.apiKey = ''
        self.apiSecret = ''
        self.settings = {}
        self.commision = 0.075
        self.notSymbols = ['MC', 'BIFI']
        # Keys: 'networks': {'coin': {'networkName': params}} - сети для определенной монеты биржи
        #       'symbols': {'symbol': {'b': baseAsset, 'q': quoteAsset'}} - Base и Quote assets символа
        #       'pairs': [symbols] - все торговые пары
        #       'data': {symbol: {'ask': ask, 'bid': bid} - данные символов ask, bid и объем
        #       'pairsMargin': [symbolsIsMargin] - все символы, котореы поддерживают маржинальную торговалю (для арбитража с хэджированием) (499)

    async def binanceAsyncGET(self, endpoint, method, params = None):
        """
        Асинхронный запрос
        """
        if method == 'public':
            url = f'https://api.binance.com{endpoint}'

            async with httpx.AsyncClient() as client:

                responce = await client.get(url)
            
                if responce.status_code == 200:
                    return responce.json()
                else:
                    raise BinanceError(responce.text, responce.status_code)
            
        if method == 'private':
            headers = {
                'X-MBX-APIKEY': self.apiKey
            }
            params['timestamp'] = int(time.time() * 1000)
            signature = hmac.new(self.apiSecret.encode('utf-8'), "&".join([f"{k}={v}" for k, v in params.items()]).encode('utf-8'), hashlib.sha256).hexdigest()
            params['signature'] = signature

            url = f'https://api.binance.com{endpoint}'
            async with httpx.AsyncClient() as client:
                responce = await client.get(url, params=params, headers=headers)

            if responce.status_code == 200:
                return responce.json()
            else:
                raise BinanceError(responce.text, responce.status_code)


    async def loadNetworks(self):
        """
        Асинхроная загрзука токенов и их сетей для депозита и вывода с биржи 
        """
        params = {
            'coin': 'USDT'
        }
        data = await self.binanceAsyncGET('/sapi/v1/capital/config/getall', 'private', params)
        try:
            settingsKeyCoins = {}
            for coin in data:
                coinAdd = coin['coin']
                networksAdd = {}
                for network in coin['networkList']:
                    try:
                        netwokParam = {
                            'eW': network['withdrawEnable'],
                            'eD': network['depositEnable'],
                            'fee': network['withdrawFee'],
                            'min': network['withdrawMin']
                        }
                        networksAdd[network['network']] = netwokParam
                    except KeyError as e:
                        raise ExchangeError('binance', e)
                settingsKeyCoins[coinAdd] = networksAdd
            self.settings['networks'] = settingsKeyCoins
        except Exception as e:
            raise BinanceError(e)

    async def loadSymbols(self):
        """
        Асинхронная загрузка символов, их Base и Quote assets.
        Асинхронная загрзука всех пар биржи
        """
        data = await self.binanceAsyncGET('/api/v3/exchangeInfo', 'public')
        settings = {}
        pairs = []
        pairsMargin = []
        for symbolBinance in data['symbols']:
            if symbolBinance['baseAsset'] not in self.notSymbols:
                if symbolBinance['status'] == 'TRADING':
                    if symbolBinance['isMarginTradingAllowed'] == True:
                        pairsMargin.append(symbolBinance['symbol'])
                    settings[symbolBinance['symbol']] = {'b': symbolBinance['baseAsset'], 'q': symbolBinance['quoteAsset']}
                    pairs.append(symbolBinance['baseAsset'] + '/' + symbolBinance['quoteAsset'])

        self.settings['symbols'] = settings
        self.settings['pairs'] = pairs
        self.settings['pairsMargin'] = pairsMargin

    def getDepositAddres(self, coin, network = None):
        """
        Запросить адрес депозита для монеты
        """
        params = {
            'coin': coin,
            'network': network,
        }
        request = self.binanceGet('/sapi/v1/capital/deposit/address', 'private', params)
        return request
    
    def getMethod(self):
        function = [self.loadNetworks, self.loadSymbols, self.loadData]
        return function
    
    def isActive(self) -> bool:
        if config['Binance'] == True:
            return True
        else:
            return False
    
    def getName(self):
        return 'Binance'
        
    def getSToSymbol(self, symbol) -> str:
        symbolAdd = self.settings['symbols'][symbol]
        data = f'https://www.binance.com/ru/trade/{symbolAdd["b"] + "_" + symbolAdd["q"]}?type=spot'
        return data
    
    async def create_margin_order(self, symbol, side, amount, price, typeOrder):
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": typeOrder.upper(),
            "quantity": str(amount),
            "timestamp": str(time.time()),
            "price": str(price)
            }
        data = await self.binanceAsyncGET('/sapi/v1/margin/order', 'private', params)
        return data
    
    async def createOrder(self, symbol, side, amount, price, typeOrder):
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": typeOrder.upper(),
            "quantity": str(amount),
            "timestamp": str(time.time()),
            "price": str(price)
            }
        data = await self.binanceAsyncGET('/api/v3/order', 'private', params)
        return data
    
    