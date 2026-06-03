from data.download import load_local_data
import pandas as pd
import streamlit as st
import os

def safe_num(val, default=0.0):
       
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def get_series(df, label):
    try:
        # 項目が存在すれば最新の値を返す
        return df.loc[label]
    except KeyError:
        # 項目名が見つからない（VISAなど）場合は None や "N/A" を返す
        return pd.Series(None, index=df.index)
    except Exception:
        # その他の予期せぬエラー（データが空など）
        return pd.Series(0, index=df.index)


def fetch_fundamentals_data(ticker: str) -> dict:
    try:
        stock = load_local_data(ticker)
        
        info = stock['info']  
        balance_sheet = stock['balance_sheet']
        #cashflow = stock['cashflow']
        financials = stock['financials']
        #history = stock['history']

        longName = info.get('longName')
        sector = info.get('sector')
        industry = info.get('industry')

        shares = safe_num(info.get('sharesOutstanding'))
        current_price = safe_num(info.get('currentPrice'))
        fiftyTwoWeekHigh = safe_num(info.get('fiftyTwoWeekHigh'))
        per = safe_num(info.get('trailingPE'))
        pbr = safe_num(info.get('priceToBook'))
        roe = safe_num(info.get('returnOnAssets')) # info内では資産利益率など複数あり
        eps = safe_num(info.get('trailingEps'))
        dividend_yield = safe_num(info.get('dividendYield'))
        net_income = safe_num(info.get('netIncomeToCommon')) #当期純利益

        market_cap = safe_num(info.get('marketCap'))
        operating_cf = safe_num(info.get('operatingCashflow'))
        fcf = safe_num(info.get('freeCashflow'))
        revenue = safe_num(info.get('totalRevenue'))
        revenue_growth = safe_num(info.get('revenueGrowth'))
        gross_profit = safe_num(info.get('grossProfits'))
        total_debt = safe_num(info.get('totalDebt'))
        total_cash = safe_num(info.get('totalCash'))
        ebitda = safe_num(info.get('ebitda'))
        forward_pe = safe_num(info.get('forwardPE'))
        peg = safe_num(info.get('pegRatio'))

        def_rev = get_series(balance_sheet, 'Current Deferred Revenue')
        rd_expense = get_series(financials, 'Research And Development')
        equity = get_series(balance_sheet, 'Stockholders Equity')
        assets = get_series(balance_sheet, 'Total Assets')

        net_debt = total_debt - total_cash
        fcf_yield = fcf / market_cap if market_cap > 0 else 0
        fcf_margin = fcf / revenue if revenue > 0 else 0
        gross_margin = gross_profit / revenue  if revenue > 0 else 0
        def_rev_yoy = def_rev.iloc[0] / def_rev.iloc[1]  - 1 if def_rev.iloc[1] > 0 else 0
        rd_ratio = rd_expense.iloc[0] / revenue  if revenue > 0 else 0
        #net_debt_ebitda = net_debt / ebitda  if ebitda > 0 else 0
        equity_ratio = equity.iloc[0] / assets.iloc[0]  if assets.iloc[0] > 0 else 0

        return {
            'ticker': ticker,
            'longName': longName,
            'sector': sector,
            'industry': industry,

            'current_price': current_price,
            '52WeekHigh': fiftyTwoWeekHigh,

            "per": per,
            'forward_pe': forward_pe,
            "pbr": pbr,
            "roe": roe,
            "eps": eps,

            'market_cap': market_cap,
            "shares": shares,
            'revenue': revenue,
            'ebitda': ebitda,
            'operating_cf': operating_cf,
            'net_income': net_income,
            'fcf': fcf,
            'gross_profit': gross_profit,
            'net_debt': net_debt,
            
            "dividend_yield": dividend_yield,
            'revenue_growth': revenue_growth,#(YoY %)

            #'total_debt': total_debt,
            #'total_cash': total_cash,

            'fcf_yield': fcf_yield,
            'fcf_margin': fcf_margin,
            'gross_margin': gross_margin,
            'rd_ratio': rd_ratio, # SpaceX評価用
            # 収益性・効率 先行指標と成長性 (Forward Looking)
            'def_rev_growth': def_rev_yoy,
            'equity_ratio': equity_ratio,

            'peg':peg,
        }
    except Exception as e:
        raise RuntimeError(f"Failed to fetch market data: {e}")

@st.cache_data
def fetch_historical_data(ticker: str) -> dict:
    try:
        stock = load_local_data(ticker)
        
        history = stock['history']
        return history
    except Exception as e:
        raise RuntimeError(f"Failed to fetch market data: {e}")
    
@st.cache_data  # キャッシュして毎回ファイルを開かないようにする
def load_ticker_map(): # --- 1. マスタデータの読み込み関数 ---

    json_path = os.path.join("config", "ticker_map.json")

    if os.path.exists(json_path): # 読み込み
        df_master = pd.read_json(json_path, orient='index')

        return df_master
    else:
        return pd.DataFrame.from_dict({
            "DGX": {
                "Ticker": "DGX",
                "LongName": "Quest Diagnostics Incorporated",
                "ShortName": "Quest Diagnostics Incorporated",
                "Sector": "Healthcare",
                "Industry": "Diagnostics & Research",
                "Website": "https://www.questdiagnostics.com"
            }
        }, orient='index') # ファイルがない場合のバックアップ用デフォルト