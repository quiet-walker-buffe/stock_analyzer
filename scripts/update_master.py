import pandas as pd
import yfinance as yf
import io
import os
import time
import requests
import json

def update_ticker_map():
    sp500_url = 'https://en.wikipedia.org/wiki/List_of_S&P_500_companies'# S&P 500の銘柄一覧をWikipediaから取得
    nikkei225_url = 'https://ja.wikipedia.org/wiki/%E6%97%A5%E7%B5%8C%E5%B9%B3%E5%9D%87%E6%A0%AA%E4%BE%A1#%E6%A7%8B%E6%88%90%E9%8A%98%E6%9F%84%E4%B8%80%E8%A6%A7'
    headers = {# ブラウザ（Chromeなど）からのアクセスに見せかけるためのヘッダー
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    response = requests.get(sp500_url, headers=headers)# 1. ページの中身を取得

    if response.status_code == 200: # 2. 取得したHTMLテキストを pandas に渡す
        tables = pd.read_html(io.StringIO(response.text))
        df = tables[0]
        sp500_tickers = df['Symbol'].tolist()
        sp500_tickers = [ticker.replace('.', '-') for ticker in sp500_tickers] # ドットが含まれるティッカー（BRK.Bなど）を yfinance 用に修正
        print(f"取得成功！銘柄数: {len(sp500_tickers)}")
    else:
        print(f"アクセス失敗: ステータスコード {response.status_code}")

    response_nikkei = requests.get(nikkei225_url, headers=headers)
    if response_nikkei.status_code == 200:
        tables = pd.read_html(io.StringIO(response_nikkei.text))
        target_tables = []
        for df in tables:
            if "証券コード" in df.columns:
                target_tables.append(df)
        df_nikkei = pd.concat(target_tables, ignore_index=True)
        df_nikkei['ticker'] = df_nikkei['証券コード'].astype(str) + ".T"
        nikkei_tickers = df_nikkei['ticker'].tolist()
        print(f"取得成功！銘柄数: {len(nikkei_tickers)}")
    else:
        print(f"アクセス失敗: ステータスコード {response_nikkei.status_code}")

    all_tickers = sp500_tickers + nikkei_tickers

    script_dir = os.path.dirname(os.path.abspath(__file__))
    CACHE_DIR = os.path.join(script_dir, "..", "config")
    os.makedirs(CACHE_DIR, exist_ok=True)

    mapping_file = 'config/ticker_map.json' # 既存のファイルを読み込む（なければ空の辞書）
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            master_map = json.load(f)
    else:
        master_map = {}
    loaded_tickers = list(master_map.keys())

    new_tickers = list(set(all_tickers) - set(loaded_tickers))
    new_data = {}
    for t in new_tickers[:100]: # まずはテスト
        time.sleep(1.0)
        print(f"Downloading {t}...")
        try:
            info = yf.Ticker(t).info
            new_data[t] = {
                "Ticker": t,
                "LongName": info.get('longName', t),
                "ShortName": info.get('shortName', t),
                "Sector": info.get('sector', 'Unknown'),
                "Industry": info.get('industry', 'Unknown'),
                "Website": info.get('website', 'N/A')
            }
        except Exception as e:
                print(f"Error fetching {t}: {e}")

    master_map.update(new_data) # 新規取得したデータをマージ# new_data が辞書形式（例: {"7203.T": {...}, "NVDA": {...}}）の場合
    sorted_map = {k: master_map[k] for k in sorted(master_map.keys())}
    with open('config/ticker_map.json', 'w', encoding='utf-8') as f: # 保存
        json.dump(sorted_map, f, indent=4, ensure_ascii=False)

    print(f"ここに保存されました: {os.path.abspath(CACHE_DIR)}")

if __name__ == "__main__":    # ファイルを直接実行（python update_master.py）した時だけここが動く
    print("単体実行モード：全銘柄の更新チェックを開始します")
    update_ticker_map()