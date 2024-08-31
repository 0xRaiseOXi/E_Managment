from .Errors import BinanceError, ExchangeError
from .Config import config
import httpx

class Gate:
    def __init__(self) -> None:
        self.apiKey = ''
        self.apiSecret = ''
        self.settings = {}
        self.commision = 0.2
        self.isMargin = False
        # Keys: 'networks': {'coin': {networks}} - сети для определенной монеты биржи
        #       'symbols': {'symbol': {'b': baseAsset, 'q': quoteAsset'}} - Base и Quote assets символа
        #       'pairs': [symbols] - все торговые пары
        #       'data': {symbol: {'ask': ask, 'bid': bid} - данные символов ask, bid и объем
    
    async def asyncGET(self, endpoint, method):
        """
        Асинхронный запрос
        """
        url = 'https://api.gateio.ws' + endpoint
        if method == 'public':
            async with httpx.AsyncClient() as client:
                headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
                responce = await client.get(url, headers=headers)

                if responce.status_code == 200:
                    return responce.json()
                else:
                    raise ExchangeError('GateIO', responce.text)

    async def loadNetworks(self) -> None:
        """
        Асинхронная загрузка сетей для вывода и депозита монет
        """
        dataDict = {}
        flagW = None
        flagD = None
        data = await self.asyncGET('/api/v4/spot/currencies', 'public')
        for symbol in data:
            if symbol['delisted'] == False:
                dataNetworkAdd = {}
                if symbol['withdraw_disabled'] == False:
                    flagW = True
                else:
                    flagW = False

                if symbol['deposit_disabled'] == False:
                    flagD = True
                else:
                    flagD = False

                networkData = {
                    'eW': flagW,
                    'eD': flagD,
                    'fee': "1",
                    'min': "15"
                }
                dataNetworkAdd[symbol['chain']] = networkData
                dataDict[symbol['currency']] = dataNetworkAdd
        self.settings['networks'] = dataDict 

    async def loadSymbols(self) -> None:
        """
        Асинхронная загрузка символов, Base и Quote assets.
        Асинхронная загрузка всех пар биржи.
        """
        symbols = {}
        pairs = []
        data = await self.asyncGET('/api/v4/spot/currency_pairs', 'public')
        for symbol in data:
            if symbol['trade_status'] == 'tradable':
                symbolSplit = symbol['id'].split('_')
                symbolAdd = symbolSplit[0] + symbolSplit[1]
                symbols[symbolAdd] = {'b': symbol['base'], 'q': symbol['quote']}
                pairs.append(symbol['base'] + '/' + symbol['quote'])
            
        self.settings['symbols'] = symbols
        self.settings['pairs'] = pairs
            

    def getName(self):
        return 'Gate'
    
    def isActive(self) -> bool:
        if config['Gate'] == True:
            return True
        else:
            return False
    
    def getSToSymbol(self, symbol) -> str:
        symbolAdd = self.settings['symbols'][symbol]
        data  = f'https://www.gate.io/ru/trade/{symbolAdd["b"] + "_" + symbolAdd["q"]}'
        return data