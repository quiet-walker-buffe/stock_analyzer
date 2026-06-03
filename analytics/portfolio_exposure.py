import yfinance as yf
from collections import Counter
from data.download import load_local_data

def calculate_sector_exposure(tickers):

    counter = Counter()

    for t in tickers:
        
        stock = load_local_data(t)
        
        info = stock['info']  

        sector = info.get("sector")

        if sector:
            counter[sector] += 1

    total = sum(counter.values())

    result = {}

    for k, v in counter.items():
        result[k] = v / total * 100

    return result