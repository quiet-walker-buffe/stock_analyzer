import yfinance as yf
import pandas as pd

def get_avg_per_pbr_4y(ticker_symbol) :
    ticker = yf.Ticker(ticker_symbol)
    
    fin = ticker.financials
    bs = ticker.balance_sheet
    history = ticker.history(period="5y", interval="1mo")['Close']

    def to_yearly_idx(series):     # まとめて年次インデックス（int）に変換する関数
        series.index = series.index.tz_localize(None).year         # タイムゾーン除去 -> インデックスを「年」の数値に変換
        return series

    metrics = pd.DataFrame({    # 財務データの準備（一括で年次化）
        'income': fin.loc['Net Income'],
        'shares': fin.loc['Diluted Average Shares'],
        'assets': bs.loc['Total Assets'],
        'liabilities': bs.loc['Total Liabilities Net Minority Interest']
    })
    metrics = to_yearly_idx(metrics) # .locで取得したSeriesをまとめて処理

    price_ave = history.resample('YE').mean()     #  株価データの年次平均化
    price_ave = to_yearly_idx(price_ave)

    df = pd.concat([price_ave, metrics], axis=1).dropna()     # 結合と計算（インデックスが「年」で一致するので自動で紐付く）
    #print(df.shape)

    market_cap = df['Close'] * df['shares']     # 時価総額 / 純利益 = PER、時価総額 / 純資産 = PBR , Market Capitalization

    per_series = market_cap / df['income']


    valid_per = per_series[per_series > 0].replace([float('inf'), float('-inf')], pd.NA).dropna() # 0より大きく、かつ有限な値だけを残す



    pbr = market_cap / (df['assets'] - df['liabilities'])

    #print(f"DEBUG: {ticker_symbol} PER={per.mean()}, PBR={pbr.mean()}")

    return valid_per.mean(), pbr.mean()
