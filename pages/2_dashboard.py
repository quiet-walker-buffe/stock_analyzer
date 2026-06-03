import streamlit as st
import pandas as pd
from data.fetch_data import fetch_fundamentals_data, fetch_historical_data
from data.visualizer import create_rich_chart
from utils import show_common_sidebar

def format_fundamentals(data):
    MILLION_KEYS = ['market_cap', 'revenue', 'net_income', 'fcf', 'ebitda', 'gross_profit'] # 100万で割るべきキーをリスト化
    for key in MILLION_KEYS:
        val = data.get(key)
        if isinstance(val, (int, float)):
            data[key] = val / 1000000
    return data

@st.cache_data
def batch_fetch_data(tickers):
    results = []
    for t in tickers:
        raw_data = fetch_fundamentals_data(t)
        raw_data = format_fundamentals(raw_data)
        results.append(raw_data)   
    df = pd.DataFrame(results)
    return df

def render_peer_dataframe(df_subset, cols_config):
    """
    df_subset: 表示したい列に絞り込んだDataFrame
    cols_config: .style.format に渡す辞書
    """
    event = st.dataframe(
        df_subset.style.format(cols_config, na_rep='N/A'),
        width='stretch',
        on_select="rerun",
        selection_mode='single-row',
        hide_index=True
    )

    # 選択イベントの処理（全タブ共通）
    if event and event.selection.rows:
        selected_row_index = event.selection.rows[0]
        # df_subset ではなく、元の df からインデックスで取得するのが確実
        new_ticker = df_subset.iloc[selected_row_index]["ticker"]
        
        if new_ticker != st.session_state.selected_ticker:
            st.rerun()


selected_ticker = None
selected_ticker = show_common_sidebar()

if selected_ticker is None:
    st.warning("⚠️ セッションの有効期限が切れました。")
    st.info("サイドバーの「銘柄検索」から再度銘柄を選択してください。自動的に分析が再開されます。")
    st.stop()

competitors = st.session_state.get("competitors", "未選択")
if competitors == "未選択":
    st.warning("competitors取得エラー")
    st.stop()
TICKERS = [selected_ticker] + competitors
df = batch_fetch_data(TICKERS)
df_history = fetch_historical_data(selected_ticker)
long_name = df['longName'].iloc[0]
sector = st.session_state.selected_sector
industry = st.session_state.selected_industry
current_price = df['current_price'].iloc[0]
last = df_history['Close'].iloc[-1]
prev = df_history['Close'].iloc[-2]
change = (last - prev) / prev * 100

st.header(f"📊 {long_name} の財務ダッシュボード  ")

st.write(f"sector:{sector}   ||industry:{industry}   ||現在の株価:{current_price}   ||前日比:{change:.2f}%")

fig = create_rich_chart(df_history, selected_ticker)
if not df_history.empty:
    st.plotly_chart(fig, width='stretch')

# データフレーム作成直後にまとめて実行
cleansing_list = ['current_price', '52WeekHigh', 'market_cap', 'per', 'forward_pe', 'peg', 'pbr', 'roe', 'fcf_yield', 
                  'revenue_growth', 'rd_ratio', 'def_rev_growth', 'fcf_margin', 'equity_ratio']
for col in cleansing_list:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce') #数値に変換し、できないものは『欠損値（NaN）』にする

tab1, tab2, tab3 = st.tabs(["基本・株価", "バリュエーション", "財務・成長性"])

with tab1:
    st.subheader("基本情報")
    cols1 = ['ticker', 'longName', 'current_price', '52WeekHigh', 'market_cap']
    if selected_ticker.endswith(".T"):
        config1 ={
            'current_price': '￥{:,.2f}',
            '52WeekHigh': '￥{:,.2f}',
            'market_cap': '￥{:,.0f}M'
        }
    else:
        config1 = {
            'current_price': '${:,.2f}',
            '52WeekHigh': '${:,.2f}',
            'market_cap': '${:,.0f}M'
        }
    render_peer_dataframe(df[cols1], config1)

with tab2:
    st.subheader("割安性・効率性指標")
    cols2 = ['ticker', 'per', 'forward_pe', 'peg', 'pbr', 'roe', 'fcf_yield']
    config2 = {
        'per': '{:.1f}x', 'forward_pe': '{:.1f}x', 'peg': '{:.2f}',
        'pbr': '{:.2f}x', 'roe': '{:.1%}', 'fcf_yield': '{:.1%}'
    }
    render_peer_dataframe(df[cols2], config2) # これだけで機能が追加される

with tab3:
    st.subheader("成長性・財務健全性")
    cols3 = ['ticker', 'revenue_growth', 'rd_ratio', 'def_rev_growth', 'fcf_margin', 'equity_ratio']
    config3 = {
        'revenue_growth': '{:.1%}', 'rd_ratio': '{:.1%}', 'def_rev_growth': '{:.1%}',
        'fcf_margin': '{:.1%}', 'equity_ratio': '{:.1%}'
    }
    render_peer_dataframe(df[cols3], config3)
