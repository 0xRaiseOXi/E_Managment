config = {
    'Binance': True,
    'Bybit': True,
    'Okx': True,
    'Bitfinex': False,
    'Kucoin': True,
    'Gate': False,
    'HTX': False,
}

marginConfig = {
    'Binance': True,
    'Bybit': True,
    'Okx': False,
    'BitFinex': False,
    'Kucoin': True,
    'GateIO': False,
    'HTX': False,
}


Networks = {
    'ERC20': 'ETH',
    'ETH': 'ETH',
    'BSC': 'BSC',
    'NEAR': 'NEAR',
    'Terra Classic': 'LUNC',
    'LUNC': 'LUNC',
    'BRC20': 'BTC',
    'BTC': 'BTC',
    'N3': 'NEO3',
    'NEO3': 'NEO3',
    'NEO': 'NEO',
    'MOVR': 'MOVR',
    'BNB': 'BNB',
    'TRC20': 'TRX',
    'TRX': 'TRX',
    'KSM': 'KSM',
    'Kusama': 'KSM',
    'Solana': 'SOL',
    'SOL': 'SOL',
    'RON': 'RON',
    'MATIC': 'MATIC',
    'RUNE': 'RUNE',
    'Omega Chain': 16,
    'OMN': 16,
    'OMEGA': 16,
    'CHZ': 17,
    'OKTC': 18,
    'Khala': 19,
    'Chiliz Legacy Chain': 20,
    'Elrond': 21,
    'Avalanche C': 22,
    'APT': 23,
    'DCR': 24,
    'ACA': 'ACA',
    'Acala': 'ACA',
    'XRP': 'XRP',
    'Theta': 'THETA',
    'Cardano': 'ADA',
    'THETA': 'THETA',
    'ADA': 'ADA',
    'Step Network': 25,
    'LUNA': 'LUNA',
    'EOS': 'EOS',
    'OAS': 'OAS',
    'OASYS': 'OAS',
    'NANO': 'NANO',
    'Polygon': 'MATIC',
    'Nano': 'NANO',
    'ARBITRUM': 'ARBI',
    'BEP20': 'BSC',
    'Enjin Relay Chain': 'RELAY',
    'XMR': 'XMR',
    'AOG': 'AOG',
    'Kadena': 'KDA',
    'LIGHTNING': 'LIGHTNING',
    'SEGWITBTC': 'SEGWITBTC',
    'DGB': 'DGB',
    'IOTA': 'IOTA',
    'MIOTA': 'IOTA',
    'SYSNEVM': 'SYSNEVM',
    'OPTIMISM': 'OP',
    'FTM': 'FTM',
    'AVAXC': 'AVAXC',
    'KAS': 'KAS',
    'ARBI': 'ARBI',
    'FSN': 'FSN',
    'KCC': 'KCC',
    'TENET': 'TENET',
    'KAVA': 'KAVA',
    'FITFI': 'FITFI',
    'CAVAX': 'CAVAX',
    'REEF': 'REEF',
    'LTC': 'LTC',
    'Arbitrum One': 'ARBI',
    'SUI': 'SUI',
    'New Economy Movement': 'XEM',
    'IOTX': 'IOTX',
    'ZKS20': 'ZKS20',
    'Monero': 'XMR',
    'XANA': 'XETA',
    'DOT': 'DOT',
    'Polygon (Bridged)': 'MATIC',
    'ALGO': 'ALGO',
    'AVAX C-Chain': 'AVAX',
    'MATIC.E': 'MATIC',
    'OP.E': 'OP',
    'MANTLE': 'MNT',
    'ARBI.E': 'ARBI',
    'OP': 'OP',
    'ZIL': 'ZIL',
    'Siacoin': 'SC',
    'BAND': 'BAND',
    'AR': 'AR',
    'ETF': 'ETF',
    'NTRN': 'NTRN',
    'QTUM': 'QTUM',
    'SCRT': 'SCRT',
    'FET': 'FET',
    'WAN': 'WAN',
    'ETC': 'ETC',
    'Ethereum Classic': 'ETC',
    'Ever': 'EVER',
    'CFXEVM': 'CFX',
    'LSK': 'LSK',
    'Conflux': 'CFX',
    'CFX': 'CFX',
    'ZKSYNC': 'ZKSYNC',
    'Arbitrum One (Bridged)': 'ARBI',
    'XTZ': 'XTZ',
    'AELF': 'ELF',
    'LTO': 'LTO',
    'XAVAX': 'XAVAX',
    'AVAX': 'AVAX',
    'FLUX': 'FLUX',
    'GLMR': 'GLMR',
    'KDA2': 'KDA',
    'KDA': 'KDA',
    'Chia': 'XCH',
    'XCH': 'XCH',
    'BCH': 'BCH',
    'Algorand': 'ALGO',
    'Horizen': 'ZEN',
    'ZEN': 'ZEN',
    'OSMO': 'OSMO',
    'KLAY': 'KLAY',
    'ZEN': 'ZEN',
    'ZKSYNCERA': 'ZKSYNCERA',
    'BASE': 'BASE',
    'ICX': 'ICON',
    'ONT': 'ONT',
    'Litecoin': 'LTC',
    'DOGE': 'DOGE',
    'FLOW': 'FLOW',
    'FIL': 'FIL',
    'Filecoin': 'FIL',
    'ONE': 'ONE',
    'EGLD': 'EGLD',
    'APTOS': 'APT',
    'CHZ2': 'CHZ',
    'RVN': 'RVN',
    'Crypto': 'Crypto',
    'ICP': 'ICP',
    'Metis': 'Metis',
    'XDC': 'XDC',
    'SEI': 'SEI',
    'Optimism (Bridged)': 'OP',
    'Optimism': 'OP',
    'Fusion': 'FSN',
    'ASTR': 'ASTR',
    'Lightning': 'LIGHTNING',
    'Bitcoin': 'BTC',
    'Lisk': 'Lisk',
    'XEC': 'XEC',
    'STRAX': 'STRAX',
    'HNT': 'HNT',
    'SYS': 'SYS',
    'ROSE': 'ROSE',
    'CORE': 'CORE',
    'Optimism': 'OP',
    'SXP': 'SXP',
    'Layer 3': 'Layer 3',
    'Chiliz Chain': 'CHZ',
    'XLM': 'XLM',
    'Stellar Lumens': 'XLM',
    'WAVES': 'WAVES',
    'ATOM': 'ATOM',
    'Dogecoin': 'DOGE',
    'OASIS': 'ROSE',
    'CELO': 'CELO',
    'Digital Cash': 'Digital Cash',
    'VET': 'VET',
    'MINA': 'MINA',
    'FEVM': 'FEVM',
    'TIA': 'TIA',
    'INJ': 'INJ',
    'COTI': 'COTI',
    'QKC': 'QKC',
    'LUNANEW': 'LUNA',
    'KAVA EVM Co-Chain': 'KAVA',
    'POKT': 'POKT',
    'Dfinity': 'Dfinity',
    'Polkadot': 'DOT',
    'TON': 'TON',
    'Ontology': 'ONT',
    'WEMIX': 'WEMIX',
    'Klaytn': 'KLAY',
    'EthereumPoW': 'ETHW',
    'ARBINOVA': 'ARBINOVA',
    'Arweave': 'AR',
    'CFX_EVM': 'CFX',
    'SC': 'SC',
    'XEM': 'XEM',
    'WAXP': 'WAXP',
    'Astar': 'ASTR',
    'KAR': 'KAR',
    'DOCK': 'DOCK',
    'Decred': 'DCR',
    'BOBA': 'BOBA',
    'Moonriver': 'MOVR',
    'DASH': 'DASH',
    'HBAR': 'HBAR',
    'Cortex': 'CTXC',
    'Moonbeam': 'GLMR',
    'Quantum': 'QTUM',
    'Zilliqa': 'ZIL',
    'Ravencoin': 'RVN',
    'Mina': 'MINA',
    'STX': 'STX',
    'Aptos': 'APT',
    'Ethereum Pow': 'ETHW',
    'WAX': 'WAXP',
    'Wax': 'WAXP',
    'METIS': 'METIS',
    'CELESTIA': 'TIA',
    'NEON3': 'NEON',
    'IOST': 'IOST',
    'CMP': 'CMP',
    'Ripple': 'XRP',
    'NULS': 'NULS',
    'Terra': 'LUNA',
    # ''
}