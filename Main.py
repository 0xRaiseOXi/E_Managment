import json
import sys
# sys.path.append("C:\PulsarRun\Run\Exchanges\ExchangesClass\Binance.py")

from .Binance import Binance
from .Bybit import Bybit
from .Okx import Okx
from .Kucoin import Kucoin
from .Gateio import Gate
from .e.Bitfinex import BitFinex
import time
import asyncio

from .Config import config
from .Config import Networks

class Main:
    def __init__(self, websocket, bot) -> None:
        self.binance = Binance()
        self.bybit = Bybit()
        self.okx = Okx()
        self.kucoin = Kucoin()
        self.gate = Gate()
        self.objectsALL = [self.binance, self.bybit, self.okx, self.kucoin, self.gate]
        self.objects = [i for i in self.objectsALL if config[i.getName()]]
        self.statusTRADE = 0
        self.websocket = websocket
        self.statusRun = 1
        self.dataTimer = {}
        self.bot = bot
        self.indexAR = 0

        self.typeALL = 0
        self.typeMARGIN = 0
        self.balance = 30

    async def run_all_methods(self, *instances):
        self.statusRun = 1
        tasks = []
        for classIn in instances:
            task = asyncio.create_task(classIn.loadNetworks())
            tasks.append(task)
            task = asyncio.create_task(classIn.loadSymbols())
            tasks.append(task)

        await asyncio.gather(*tasks)
        await self.runIteration()

    async def loadingDataServerJava(self):
        dataArray = await self.websocket.getData()
        data = json.loads(dataArray[0])
        
        def replace_keys(exchange, symbol):
            new_dict = {}
            for key, value in data[exchange].items():
                new_key = key.replace(symbol, '')
                new_dict[new_key] = value
            return new_dict
        
        for i in self.objects:
            if i.getName() == 'Kucoin':
                data['Kucoin'] = replace_keys('Kucoin', '-')
            if i.getName() == 'Okx':
                data['Okx'] = replace_keys('Okx', '-')
            if i.getName() == 'Gate':
                data['Gate'] = replace_keys('Gate', '_')

            i.settings['data'] = data[i.getName()]

        return data

    def buildExchanges(self) -> list:
        exchanges = []
        for object in self.objects:
            if object.isActive() == True:
                exchanges.append(object)
        return exchanges

    def buildSymbols(self):

        keysSymbols = set()
        keysBaseAsset = set()

        for exchange in self.objects:
            for key in exchange.settings['symbols'].keys():
                keysSymbols.add(key)
                value = exchange.settings['symbols'][key]['b']
                keysBaseAsset.add(value)
        """
        {coin: {exchange: {symbols}}}
        """
        symbolsExchange = {}
        for keyCoin in keysBaseAsset:
            symbolsExchangeAdd = {}
            for exchange in self.objects:
                symbols = []
                for item, data in exchange.settings['symbols'].items():
                    if keyCoin == data['b']:
                        exchangeName = exchange.getName()
                        symbols.append(item)
                symbolsExchangeAdd[exchange] = symbols
            symbolsExchange[keyCoin] = symbolsExchangeAdd
        return symbolsExchange
    
    async def runIteration(self):
        symbols = self.buildSymbols()
        while self.statusRun == 1:
            error = 0
            data = await self.loadingDataServerJava()
            symbolSTATE = {}
            for symbol, data in symbols.items():
                dataExchange = {}
                for objectExchange, symbolsExchange in data.items():
                    symbolsEx = {}
                    symbolSTATEAdd = {}
                    if len(symbolsExchange) != 0:

                        for coin in symbolsExchange:

                            if self.statusTRADE == 1:
                                if coin not in objectExchange.settings['pairsMargin']:
                                    continue

                            try :
                                ask = objectExchange.settings['data'][coin]['a']
                                bid = objectExchange.settings['data'][coin]['b']

                                settingsSymbol = objectExchange.settings['symbols'][coin]['q']

                                if settingsSymbol != 'USDT':
                                    try:
                                        symbol2 = settingsSymbol + 'USDT'
                                        ask_symbol2USDT = objectExchange.settings['data'][symbol2]['a']
                                        bid_symbol2USDT = objectExchange.settings['data'][symbol2]['b']

                                        askKey = float(ask) * float(ask_symbol2USDT)
                                        bidKey = float(bid) * float(bid_symbol2USDT)
                                    except KeyError:
                                        symbol2 = 'USDT' + settingsSymbol 
                                        ask_symbol2USDT = objectExchange.settings['data'][symbol2]['b']
                                        bid_symbol2USDT = objectExchange.settings['data'][symbol2]['a']

                                        askKey = float(ask) / float(ask_symbol2USDT)
                                        bidKey = float(bid) / float(bid_symbol2USDT)

                                    symbolsEx[coin] = {'a': askKey, 'b': bidKey}
                                else:
                                    symbolsEx[coin] = {'a': ask, 'b': bid}

                                symbolSTATEAdd[coin] = {'a': ask, 'b': bid}
                            except KeyError as e:
                                error += 1
                                continue

                    symbolSTATE[objectExchange.getName()] = symbolSTATEAdd                
                    dataExchange[objectExchange] = symbolsEx

                minAsk = 0
                maxBid = 0
                askExchange = None
                bidExchange = None

                for ExchangeObject, dataExchange in dataExchange.items():
                    if dataExchange:
                        minKey = min(dataExchange, key=lambda k: float(dataExchange[k]['a']))
                        maxKey = min(dataExchange, key=lambda k: float(dataExchange[k]['b']))

                        if minAsk == 0 and maxBid == 0:
                            minAsk = dataExchange[minKey]['a']
                            maxBid = dataExchange[maxKey]['b']
                            askExchange = ExchangeObject
                            bidExchange = ExchangeObject
                        else:
                            askIteration = dataExchange[minKey]['a']
                            if float(askIteration) < float(minAsk):
                                minAsk = float(askIteration)
                                askExchange = ExchangeObject
                                
                            bidIteartion = dataExchange[maxKey]['b']
                            if float(bidIteartion) > float(maxBid):
                                maxBid = float(bidIteartion)
                                bidExchange = ExchangeObject
                       
                        if askExchange.getName() != bidExchange.getName():
                            try :
                                askVolume = float(askExchange.settings['data'][minKey]['A']) * float(minAsk)
                                bidVolume = float(bidExchange.settings['data'][maxKey]['B']) * float(maxBid)

                                if minKey[-4:] == 'USDT':
                                    if askVolume < self.balance:

                                        if bidVolume < askVolume:
                                            iterA = bidVolume / float(minAsk) * (1 - 0.1 / 100)
                                        else:
                                            iterA = askVolume / float(minAsk) * (1 - 0.1 / 100)
                                    else:
                                        iterA = self.balance / float(minAsk) * (1 - 0.1 / 100)
                                else:
                                    if askVolume < self.balance:
                                        if bidVolume < askVolume:
                                            iterA = bidVolume / float(minAsk) * (1 - 0.2 / 100)
                                        else:
                                            iterA = askVolume / float(minAsk) * (1 - 0.2 / 100)
                                    else:
                                        iterA = self.balance / float(minAsk) * (1 - 0.2 / 100)

                            except KeyError:
                                error += 1
                                pass
                            try :
                                coinAsk = askExchange.settings['symbols'][minKey]['b']
                                coinBid = bidExchange.settings['symbols'][maxKey]['b']

                                exchangeA = askExchange.settings['networks'][coinAsk]
                                exchangeB = bidExchange.settings['networks'][coinBid]

                                def iterationNetworks():
                                    
                                    networksData = {}
                                    for networkKey, value in exchangeA.items():
                                        try :
                                            networkConfig = Networks[networkKey]

                                            for networkKeyB, valueB in exchangeB.items():
                                                networkConfigB = Networks[networkKeyB]
                                                
                                                if networkConfig == networkConfigB:
                                                    if value['eW'] == True and valueB['eD'] == True:
                                                            networksData[networkKey] = {'nB': networkKeyB, 'fee': value['fee'], 'min': value['min']}
                                        except KeyError as e:
                                            print('Netwrok error:', e)
                                        
                                    networkAsk = None
                                    networkBid = None
                                    networkCommision = None
                                    networkMin = None

                                    if networksData:
                                        for networkName, networkValue in networksData.items():
                                        
                                            if networkCommision != None:

                                                if networkValue['fee'] < networkCommision:
                                                    networkAsk = networkName
                                                    networkBid = networkValue['nB']
                                                    networkCommision = networkValue['fee']
                                                    networkMin = networkValue['min']
                                            else:
                                                networkAsk = networkName
                                                networkBid = networkValue['nB']
                                                networkCommision = networkValue['fee']
                                                networkMin = networkValue['min']

                                        dataNetwork = {'nA': networkAsk, 'nB': networkBid, 'fee': networkCommision, 'min': networkMin}
                                        return dataNetwork
                            
                                    
                                dataNetworkSUCCESS = iterationNetworks()

                                if dataNetworkSUCCESS:
                                    iterA -= float(dataNetworkSUCCESS['fee'])

                                    if maxKey[-4:] == 'USDT':

                                        iterB = float(iterA) * (1 - 0.1 / 100)
                                    else:
                                        iterB = float(iterA) * (1 - 0.2 / 100)

                                    end = float(iterB) * float(maxBid)

                                    if end - self.balance > 0.1:
                                        try:
                                            timestart = self.dataTimer[minKey + maxKey]['timestart']
                                            if time.time() - timestart > 300:
                                                print('____________________________')
                                                print(minKey, minAsk, maxKey, maxBid, askExchange.getName(), "--->", bidExchange.getName(), end)
                                                print('____________________________')
                                                self.dataTimer[minKey + maxKey] = {'timestart': time.time()}
                                                await self.sendMessage(end - self.balance, askExchange, bidExchange, minKey, maxKey, minAsk, maxBid, dataNetworkSUCCESS['nA'] + '/' + dataNetworkSUCCESS['nB'], dataNetworkSUCCESS['fee'], float(dataNetworkSUCCESS['min']) * float(minAsk), symbolSTATE[askExchange.getName()][minKey]['a'], symbolSTATE[bidExchange.getName()][maxKey]['b'])

                                        except KeyError:
                                            print('____________________________')
                                            print(minKey, minAsk, maxKey, maxBid, askExchange.getName(), "--->", bidExchange.getName(), end)
                                            print('____________________________')
                                            self.dataTimer[minKey + maxKey] = {'timestart': time.time()}
                
                                            await self.sendMessage(end - self.balance, askExchange, bidExchange, minKey, maxKey, minAsk, maxBid, dataNetworkSUCCESS['nA'] + '/' + dataNetworkSUCCESS['nB'], dataNetworkSUCCESS['fee'], float(dataNetworkSUCCESS['min']) * float(minAsk), symbolSTATE[askExchange.getName()][minKey]['a'], symbolSTATE[bidExchange.getName()][maxKey]['b'])
                                            
                            except KeyError as e:
                                print(e)
                                pass
            print(error)

        
    async def createOrder(self, symbolAsk, exchangeAsk, symbolBid, exchangeBid):
    
        order = exchangeAsk.create_order(symbolAsk)

    async def sendMessage(self, end, exchangeA, exchangeB, symbol, symbol2, price, price2, network, networkFee, networkMin, askO, bidO):
        self.indexAR += 1
        print("Отправляю сообщение")
        if symbol2 in exchangeB.settings['pairsMargin']:
            self.typeMARGIN += 1
        else:
            self.typeALL += 1

        message = f'Арбитраж возможность {self.indexAR}\n\n{symbol} {price}  -->  {symbol2} {price2} ({str(end)[:4] + "%"})\nБиржа покупки: <a href="{exchangeA.getSToSymbol(symbol)}">{exchangeA.getName()}</a>\nЦена покупки: {askO}\nОбъём покупки: {exchangeA.settings[symbol]["A"]}\nБиржа продажи: <a href="{exchangeB.getSToSymbol(symbol2)}">{exchangeB.getName()}</a>\nЦена продажи: {bidO}\nОбъем продажи: {exchangeB.settings[symbol2]["B"]}\n\nСеть: {network}\nКоммисия сети: {networkFee}\nМинимальная сумма: {networkMin}\n\nТокены: {self.typeALL}\nМаржинальные токены: {self.typeMARGIN}'
        print("Отправляю сообщение 2")
        await self.bot.send_message(chat_id=1070221127, text=message, parse_mode="HTML", disable_web_page_preview=True)

    async def async_run(self):
        await self.run_all_methods(*self.buildExchanges())

    def run(self):
        asyncio.run(self.run_all_methods(*self.buildExchanges()))