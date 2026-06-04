import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from analytics.score_engine import calculate_quority_score
from data.fetch_data import fetch_fundamentals_data
from services.ai_service import call_gemini, get_prompt
from utils import show_common_sidebar
from data.download import load_local_data

def draw_radar_chart(df, selected_ticker, competitors, categories):
    selected_ticker_data = df[df['ticker'] == selected_ticker] # 選択された銘柄のデータを抽出
    selected_values = selected_ticker_data[categories].values.flatten().tolist()
    
    sector_df = df[df['ticker'].isin(competitors)]
    sector_avg_series = sector_df[categories].mean()
    sector_avg_values = sector_avg_series.tolist()

    selected_values += selected_values[:1] # レーダーチャートを閉じるために、最初の要素を最後に追加
    sector_avg_values += sector_avg_values[:1]
    plot_categories = categories + [categories[0]]

    fig = go.Figure()

    # セクター平均（背面に配置）
    fig.add_trace(go.Scatterpolar(
        r=sector_avg_values,
        theta=plot_categories,
        name='Sector Avg',
        line=dict(color='gray', dash='dash'), # グレーの点線
        fill='none'
    ))

    # 選択銘柄（前面に配置）
    fig.add_trace(go.Scatterpolar(
        r=selected_values,
        theta=plot_categories,
        name=selected_ticker,
        fill='toself',
        line=dict(color="#948AE7", width=3)   # 濃い枠線
    ))
    fig.update_layout(
        height=280,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="#f0f0f0"),
            angularaxis=dict(
                gridcolor="#f0f0f0",
                rotation=90, # 12時方向スタート
                direction='clockwise'   # 右回り（時計回り）)
            ),
        ),
        showlegend=True,
        margin=dict(l=70, r=20, t=0, b=0)
    )
    st.plotly_chart(fig, width='stretch')

@st.cache_data 
def get_score_data(tickers):
    results = []
    for t in tickers:
        raw_data = fetch_fundamentals_data(t)
        score_data = calculate_quority_score(raw_data)
        score_data = offset_score(score_data)
        results.append(score_data)
    df = pd.DataFrame(results)
    return df

def offset_score(data):
    for key, value in data.items():
        if isinstance(value, (int, float)): 
            value = 1 + value * 0.9
            data[key] = round(value, 1)
    return data

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
df = get_score_data(TICKERS) 

if selected_ticker:
    stock = load_local_data(selected_ticker)
    info = stock['info']  
    longName = info.get('longName') 
    st.subheader(f"{longName}のスコアチャート")

col1, col2, col3,col4 = st.columns([1, 1, 1, 1]) # 画面を分割

with col1:
    st.write("【P/L (損益計算書)】")
    categories1 = [
        'Revenue Growth',
        'Gross Margin',
        'R&D / Revenue',
    ]
    draw_radar_chart(df, selected_ticker, competitors, categories1)
with col2: 
    st.write("【B/S (貸借対照表)】")
    categories2 = [
        'Equity Ratio',
        'Def. Rev Growth',
        'Net Cash Ratio',
    ]
    draw_radar_chart(df, selected_ticker, competitors, categories2)
with col3:
    st.write("【C/F (キャッシュフロー)】")
    categories3 = [
        'OCF / Net Income',
        'FCF Margin',
        'FCF Yield',
    ]
    draw_radar_chart(df, selected_ticker, competitors, categories3)
with col4:
    st.subheader("🤖 AI Stock Critic")
    selected_data = df[df['ticker'] == selected_ticker].iloc[0]     # 選択されている銘柄のデータを準備
    #print(f"selected_data:{selected_data}")

    if st.button(f"{selected_ticker} をAI診断する"):
        with st.spinner("Geminiが財務諸表を読み解いています..."):
            prompt = get_prompt(selected_data)
            analysis = call_gemini(prompt) # 診断実行
            st.info(analysis)
            print(analysis)

st.caption("📊 スコアリング基準(10点満点中満点条件)")
st.caption("P/L: Revenue Growth(10%+)   Gross Margin(40%+)            R&D / Revenue(15%+)")
st.caption("B/S: Equity Ratio(30%+)     Deferred Revenue Growth(5%+)  net cash ratio(10%+)")
st.caption("C/F: OCF / Net Income(1.0+) FCF Margin(15%+)              FCF Yield(7%+)")
    
event = st.dataframe( # データフレームを表示し、選択を有効にする
    df,
    width='stretch',
    on_select="rerun",  # 選択されたら即座に再実行
    selection_mode='single-row', # 1行だけ選べるようにする
    hide_index=True
)

if event and event.selection.rows: # 選択された行からティッカーを抽出して更新
    selected_row_index = event.selection.rows[0]
    new_ticker = df.iloc[selected_row_index]["ticker"] # "Ticker"カラムから取得
    
    if new_ticker != st.session_state.selected_ticker:
        st.rerun() # 新しい銘柄でページ全体をリロード

