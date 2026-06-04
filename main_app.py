import streamlit as st
from data.fetch_data import fetch_historical_data
from data.scan_data import fetch_market_context
import pandas as pd
from datetime import datetime, timedelta
from data.visualizer import create_rich_chart
from scripts.update_master import update_ticker_map

st.set_page_config( # ページ全体の基本設定
    page_title="Investment Quality Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data(ttl=300)
def cached_market_context():
    return fetch_market_context()

@st.cache_data(ttl=600)
def cached_historical_data(ticker: str):
    return fetch_historical_data(ticker)

def main():
    st.sidebar.button("🔄 Update Ticker Map", on_click=update_ticker_map) # サイドバーに更新ボタンを追加
    st.title("Welcome to Quality Scanner 🚀") # メイン画面のウェルカムメッセージ
    
    st.markdown("""
     このツールについて
    このアプリは、財務データを独自アルゴリズムでスコアリングし、「価値ある株」の可視化を目指したツールです。
    左側のサイドバーから各機能を選択してください：
    * **scoreboard**: 財務スコアのレーダチャートとAI診断          
    * **dashboard**: 株価推移と柄主要データ競合比較    
    * **financial_charts**: 財務諸表データ表示
    """)

    try:
        data = cached_market_context()
    except Exception as exc:
        st.error(f"マーケットデータの取得に失敗しました: {exc}")
        return

    if not data:
        st.warning("マーケットコンテキストデータが取得できませんでした。")
        return

    ticker_names = ["S&P 500", "NASDAQ", "NY DOW", "VIX", "US10Y", "DXY"]
    st_cols = st.columns(len(ticker_names)) # 2. Streamlitの列オブジェクトを作成（銘柄の数だけ作る）
    for col_object, name in zip(st_cols, ticker_names): # 3. zip関数を使って「列」と「名前」をセットで取り出す
        d = data.get(name, {})  # name は "S&P 500" などの文字列
        price = d.get('price')
        change = d.get('change')
        with col_object: # col_object は Streamlit のレイアウト枠
            if price is None or change is None:
                st.write("データなし")
            else:
                st.metric(
                    label=name,
                    value=f"{price:.2f}",
                    delta=f"{change:.2f}%"
                )
    st.subheader("Market Trend (S&P 500)")

    try:
        full_df = cached_historical_data("^GSPC")
    except Exception as exc:
        st.error(f"ヒストリカルデータの取得に失敗しました: {exc}")
        return

    if full_df is None or full_df.empty:
        st.warning("株価履歴データがありません。")
        return

    full_df.index = full_df.index.tz_localize(None)
    period_choice = st.segmented_control( # ユーザーが期間を選択
        "表示期間",
        options=["1M", "6M", "1Y", "3Y", "5Y", "YTD"],
        default="1Y"
    )

    end_date = full_df.index[-1] # 最新の日付 # 選択に応じてスライシング

    if period_choice == "YTD":
        start_date = datetime(end_date.year, 1, 1)
    else:
        period_map = {"1M": 30, "6M": 180, "1Y": 365, "3Y": 1095, "5Y": 1825} # 期間を日数に換算して計算
        days = period_map.get(period_choice, 365)
        start_date = end_date - timedelta(days=days)
    
    display_df = full_df[full_df.index >= pd.to_datetime(start_date)] # ここがポイント：ローカルデータから必要な分だけ切り出す

    if display_df.empty:
        st.warning("選択した期間に表示できるデータがありません。")
        return

    st.plotly_chart(create_rich_chart(display_df, "^GSPC")) # チャート表示

if __name__ == "__main__":
    main()