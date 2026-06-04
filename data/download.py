import yfinance as yf
import pickle
import os
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(CURRENT_DIR, "../cache") # 必要に応じて階層を調整


def download_ticker(ticker):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    print(f"Downloading {ticker}...")
    try:
        t = yf.Ticker(ticker)
        
        # 既存の計算（PER, ROE, 株式数など）に必要なデータを全て抽出
        data_bundle = {
            "info": t.info,
            "history": t.history(period="4y"),          # 株価推移
            "financials": t.financials,                # 損益計算書（PL）
            "quarterly_financials": t.quarterly_financials,  
            "cashflow": t.cashflow,                    # キャッシュフロー（CF）
            "quarterly_cashflow": t.quarterly_cashflow,   
            "balance_sheet": t.balance_sheet,          # 貸借対照表（BS）
            "quarterly_balance_sheet": t.quarterly_balance_sheet, 
            "last_updated": time.time()
        }
        
        with open(f"{CACHE_DIR}/{ticker}.pkl", "wb") as f:
            pickle.dump(data_bundle, f)
            
        print(f"✅ Saved: {CACHE_DIR}/{ticker}.pkl")
        time.sleep(0.1) # サーバーへの負荷を軽減するため、少し待機
        return True
    except Exception as e:
        print(f"❌ Failed to download {ticker}: {e}")
        return False

def load_local_data(ticker):
    file_path = f"{CACHE_DIR}/{ticker}.pkl"

    if os.path.exists(file_path): # 判定1: ファイルが存在し、かつ「新しければ」ロード
        last_modified = os.path.getmtime(file_path) # ファイルの更新日時を確認
        if time.time() - last_modified < 86400:  # 24時間 以内
            print(f"Loading {ticker} from local cache...")
            with open(file_path, "rb") as f:
                return pickle.load(f)

    download_ticker(ticker)

    with open(file_path, "rb") as f:
        return pickle.load(f)
