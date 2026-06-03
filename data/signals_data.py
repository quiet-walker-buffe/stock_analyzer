import yfinance as yf
from data.download import load_local_data
from data.analyze_data import get_robust_data

def fetch_signals_data(ticker: str) -> dict:
    try:
        stock = load_local_data(ticker)
        
        info = stock['info']  
        cashflow = stock['cashflow']
        financials = stock['financials']
        balance_sheet = stock['balance_sheet']

        fcf_labels = ['Free Cash Flow', 'Repurchase Of Capital Stock']
        operating_cf_labels = ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities']
        net_income_labels = ['Net Income', 'Net Income Common Stockholders']
        total_debt_labels = ['Total Debt', 'Long Term Debt']
        cash_equivalents_labels = ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments']
        dividend_labels = ['Cash Dividends Paid', 'Common Stock Dividend Paid', 'Dividends Paid']
        buyback_labels = ['Repurchase Of Capital Stock', 'Common Stock Repurchased', 'Common Stock Retirement']

        pbr = info['priceToBook']
        roe = info['returnOnAssets'] # info内では資産利益率など複数あり
        market_cap = info['marketCap']
        ebitda = info['ebitda']
        total_debt = info['totalDebt']
        total_cash = info['totalCash']
        fcf = get_robust_data(cashflow, fcf_labels)
        operating_cf = get_robust_data(cashflow, operating_cf_labels)
        dividend_payment = get_robust_data(cashflow, dividend_labels)
        stock_buyback = get_robust_data(cashflow, buyback_labels)
        net_income = get_robust_data(financials, net_income_labels)
        total_debt = get_robust_data(balance_sheet, total_debt_labels)
        cash_equivalents = get_robust_data(balance_sheet, cash_equivalents_labels)

        bond_yield = yf.Ticker("^TNX").info['regularMarketPrice']

        return {
            "pbr": pbr,
            "roe": roe,
            "market_cap": market_cap,
            "ebitda": ebitda,
            "total_debt": total_debt,
            "total_cash": total_cash,
            "fcf": fcf,
            "operating_cf": operating_cf,
            "net_income": net_income,
            "cash_equivalents": cash_equivalents,
            "dividend_payment": dividend_payment,
            "stock_buyback": stock_buyback,
            "bond_yield": bond_yield,
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")