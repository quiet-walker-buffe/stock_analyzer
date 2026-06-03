import traceback
import streamlit as st
import yfinance as yf   
from analytics.growth_layer import revenue_cagr, apply_growth_modifier
from analytics.score_engine import compute_signal_score
from config.tickers import AI
from analytics.detect import classify_volume_spike
from config.market_context import MARKET_SYMBOLS
from data.download import load_local_data

@st.cache_data
def fetch_market_context():

    data = {}

    for name, symbol in MARKET_SYMBOLS.items():
        try:
            stock = yf.Ticker(symbol)
            fast_info = stock.fast_info
            price = fast_info.last_price
            prev = fast_info.previous_close
        except Exception as e:
            raise RuntimeError(f"Failed to fetch market data: {e}")


        if price and prev:
            change = (price - prev) / prev * 100
        else:
            change = 0

        data[name] = {
            "price": price,
            "change": change,
        }

    return data

def fetch_scan_data(ticker: str) -> dict:
    try:
        stock = load_local_data(ticker)
        
        info = stock['info']  
        cashflow = stock['cashflow']
        financials = stock['financials']
        history = stock['history']

        shares = info.get('sharesOutstanding')
        current_price = info.get('currentPrice')
        current_volume = info.get('volume')
        avg_volume = info.get('averageVolume')
        per = info.get('trailingPE')
        pbr = info.get('priceToBook')
        roe = info.get('returnOnAssets') # info内では資産利益率など複数あり
        #eps = info.get('trailingEps'),
        dividend_yield = info.get('dividendYield', 0.0)
        net_income = info.get('netIncomeToCommon') #当期純利益

        if history.empty or len(history) < 2:
            if cashflow.empty or len(cashflow) < 1:
                raise ValueError("Insufficient market data.")

        prev_close = history['Close'].iloc[-2]
        operating_cf = cashflow.loc['Operating Cash Flow'].iloc[0]

        growth_rate = revenue_cagr(stock) #過去３年間での年間成長率
        pct_change = ((current_price - prev_close) / prev_close) * 100
        rvol = current_volume / avg_volume if avg_volume else 0
        volume_flag = classify_volume_spike(rvol)

        return {
            "current_price": current_price,
            "volume": current_volume,
            "pct_change": pct_change,
            "rvol": rvol,
            "volume_flag": volume_flag,
            "operating_cf": operating_cf,
            "per": per,
            "pbr": pbr,
            "roe": roe,
            "growth_rate": growth_rate,
            "dividend_yield": dividend_yield,
            "net_income": net_income,
            "shares": shares
        }

    except Exception as e:
        raise RuntimeError(f"Failed to fetch market data: {e}")
    
def create_results(tickers):
    results = []

    for ticker in tickers:
        try:
            #print(f"DEBUG: Processing {ticker}...")
            final_score = 0
            data = fetch_scan_data(ticker)
            score = compute_signal_score(data) #テクニカル
            final_score = apply_growth_modifier(
                ticker,
                score,
                AI
            )
            results.append((ticker, data, final_score))
            #print(f"DEBUG: Successfully added {ticker}")
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            traceback.print_exc()
            continue

    results.sort(key=lambda x: x[2], reverse=True)
    return results
