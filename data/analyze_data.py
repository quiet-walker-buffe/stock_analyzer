import yfinance as yf
import pandas as pd
from analytics.analyze_engine import get_growth_metrics
from data.download import load_local_data

def get_robust_data(df, labels):
    """
    複数のラベルから存在するものを探し、Seriesとして返す。
    一つも見つからなければ全期間0のSeriesを返す。
    """
    for label in labels:
        if label in df.index:
            # yfinanceのデータが空(NaN)でないか確認して取得
            series = df.loc[label]
            if not series.dropna().empty:
                return series
    return pd.Series(0, index=df.columns)

def fetch_analyze_data(ticker):
    try:
        stock = load_local_data(ticker)
        
        cashflow = stock['quarterly_cashflow']
        financials = stock['quarterly_financials']
        balance_sheet = stock['quarterly_balance_sheet']

        op_cf_labels = ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities']
        capex_labels = ['Capital Expenditure', 'Investments In Property Plant And Equipment']
        revenue_labels = ['Total Revenue', 'Operating Revenue', 'Revenue']
        equity_labels = ['Stockholders Equity', 'Total Equity Gross Minority Interest', 'Common Stock Equity', 'Total Stockholders Equity']
        ap_labels = ['Accounts Payable', 'Payables', 'Payables And Accrued Expenses', 'Total Tax Payable']
        cl_labels = ['Current Deferred Revenue', 'Deferred Revenue', 'Contract Liabilities', 'Other Current Liabilities']
        cost_of_revenue_labels = ['Cost Of Revenue',  'Cost of Revenue', 'Cost of Services', 'Cost of Goods Sold']

        op_cf = get_robust_data(cashflow, op_cf_labels) #営業キャッシュフロー
        capex = get_robust_data(cashflow, capex_labels) #資本的支出、設備投資
        revenue = get_robust_data(financials, revenue_labels) #総収入 
        equity = get_robust_data(balance_sheet, equity_labels) #純資産、株主資本
        assets = balance_sheet.loc['Total Assets'] #経済的価値のある財産
        net_income = financials.loc['Net Income'] #当期純利益
        accounts_payable = get_robust_data(balance_sheet, ap_labels) #買掛金、未払いの代金
        total_current_liabilities = balance_sheet.loc['Current Liabilities'] #流動負債
        accrued_expenses = balance_sheet.loc['Payables And Accrued Expenses'] #未払費用
        cl = get_robust_data(balance_sheet, cl_labels)
        cost_of_revenue = get_robust_data(financials, cost_of_revenue_labels) #売上原価

        try:
            inventory = balance_sheet.loc['Inventory'] #在庫
            
            dsi = (inventory / cost_of_revenue * 90).sort_index(ascending=False) # 在庫回転期間 (DSI) 
        except KeyError:
            inventory = pd.Series([0.0])  #在庫データの取得（在庫がない企業は0とする）
            dsi = pd.Series([0.0])

        fcf = (op_cf - abs(capex)).sort_index(ascending=False)  #（CapExがマイナスであることを想定し、明示的に引く）
        fcf_margin = (fcf / revenue * 100).sort_index(ascending=False)

        equity_ratio = (equity / assets * 100).sort_index(ascending=False)  #自己資本比率
        cl_ratio = (cl / revenue).sort_index(ascending=False)  #収益転換倍率
        good_debt_ratio = ((cl + accounts_payable) / total_current_liabilities).sort_index(ascending=False)

        fcf_growth_qoq, fcf_growth_yoy = get_growth_metrics(fcf)
        revenue_growth_qoq, revenue_growth_yoy = get_growth_metrics(revenue)
        cl_growth_qoq, cl_growth_yoy = get_growth_metrics(cl)
        accrued_growth_qoq, accrued_growth_yoy = get_growth_metrics(accrued_expenses)

        gross_margin_ratio = ((revenue - cost_of_revenue)/ revenue).sort_index(ascending=False)


        metrics = {
        'ticker': ticker,
        'op_cf': op_cf,
        'capex': capex,
        'revenue': revenue,
        'equity': equity,
        'assets': assets,
        'net_income': net_income,
        'accounts_payable': accounts_payable,
        'total_current_liabilities': total_current_liabilities,
        'accrued_expenses': accrued_expenses,
        'cl': cl,
        'inventory': inventory,
        'cost_of_revenue': cost_of_revenue,
        'dsi': dsi,
        'fcf': fcf,
        'fcf_margin': fcf_margin,
        'equity_ratio': equity_ratio,
        'cl_ratio': cl_ratio,
        'good_debt_ratio': good_debt_ratio,
        'fcf_growth_qoq': fcf_growth_qoq,
        'fcf_growth_yoy': fcf_growth_yoy,
        'revenue_growth_qoq': revenue_growth_qoq,
        'revenue_growth_yoy': revenue_growth_yoy,
        'cl_growth_qoq': cl_growth_qoq,
        'cl_growth_yoy': cl_growth_yoy,
        'accrued_growth_qoq': accrued_growth_qoq,
        'accrued_growth_yoy': accrued_growth_yoy,
        'gross_margin_ratio': gross_margin_ratio,
        
        }
        #print(metrics['ticker'])
        return metrics
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")

