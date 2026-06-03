import pandas as pd
import plotly.express as px
import streamlit as st
from data.download import load_local_data
from utils import show_common_sidebar

def draw_chart(df_chart, rows):
    df_chart = df_chart.sort_index(ascending=True)

    fig = px.bar(
        df_chart.reset_index().rename(columns={'index': 'Date'}),
        x='Date',
        y=rows,
    )
    

    fig.update_layout(
        
        template='plotly_dark',
        plot_bgcolor='#111111',  
        paper_bgcolor='#111111',
        yaxis_title="Amount",
        legend_title="Metric",
        barmode='group',
        font=dict(
            color="white",
            family="Arial, sans-serif",
            size=12
        ),
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:,.0f}<extra></extra>")
    st.plotly_chart(fig, width='stretch', theme=None) 

def index_is(period_choice, df_chart):
    if period_choice == "Annual (年次)":
        return df_chart.index.strftime('%Y')
    else:
        return df_chart.index.strftime('%Y-%m') # 四半期は「年-月」


selected_ticker = None
selected_ticker = show_common_sidebar()

if selected_ticker is None:
    st.warning("⚠️ セッションの有効期限が切れました。")
    st.info("サイドバーの「銘柄検索」から再度銘柄を選択してください。自動的に分析が再開されます。")
    st.stop()

if selected_ticker:
    stock = load_local_data(selected_ticker)
    info = stock['info']  
    longName = info.get('longName') 
    st.subheader(f"{longName}")
    tab1, tab2, tab3 = st.tabs(["損益計算書 (P&L)", "貸借対照表 (B/S)", "キャッシュフロー (C/F)"])
        
    with tab1:
        period_choice = st.radio("P&L Period Select", ["Annual (年次)", "Quarterly (四半期)"], horizontal=True)
        if period_choice == "Annual (年次)":
            df_raw = stock['financials']
            title_suffix = "(Annual)"
        else:
            df_raw = stock['quarterly_financials']
            title_suffix = "(Quarterly)"

        if not df_raw.empty:
            target_rows = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA"]
            available_rows = [r for r in target_rows if r in df_raw.index] # 存在する項目だけを安全に抽出
            df_filtered = df_raw.loc[available_rows]
            df_chart = df_filtered.T # グラフ用にデータを整形（転置
            df_chart.index = index_is(period_choice, df_chart)

        else:
            st.warning("財務データが見つかりませんでした。")
        draw_chart(df_chart, target_rows)
        st.write("### Income Statement")
        if not df_raw.empty:
            st.dataframe(df_raw)
        else:
            st.warning("データが取得できませんでした")
                
    with tab2:
        period_choice = st.radio("B/S Period Select", ["Annual (年次)", "Quarterly (四半期)"], horizontal=True)
        if period_choice == "Annual (年次)":
            df_raw = stock['balance_sheet']
            title_suffix = "(Annual)"
        else:
            df_raw = stock['quarterly_balance_sheet']
            title_suffix = "(Quarterly)"
        
        bs_mapping = { # 1. 表記揺れに対応するマッピング辞書を定義
            "Total Assets": ["Total Assets"],
            "Total Liabilities": ["Total Liabilities Net Minority Interest", "Total Liabilities", "Total LiabilitiesNetMin"],
            "Stockholders Equity": ["Stockholders Equity", "Total Equity Gross Minority Interest", "Total Stockholders Equity"],
            "Cash & Cash Equivalents": ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments", "Cash"],
            "Total Debt": ["Total Debt", "Long Term Debt", "Total Long Term Debt"]
        }


        df_bs_filtered = pd.DataFrame() # yfinanceの生データから、存在する項目を名寄せして抽出

        for custom_name, yf_keys in bs_mapping.items():
            for key in yf_keys:
                if key in df_raw.index:
                    
                    df_bs_filtered[custom_name] = df_raw.loc[key] # 見つけた最初のキーのデータを、カスタム名（綺麗な名前）で格納
                    break # 1つ見つかったら次の項目へ
        df_bs_chart = df_bs_filtered.copy() # この時点で df_bs_filtered はすでに「日付」がインデックス、項目名がカラムになっています
        df_bs_chart.index = index_is(period_choice, df_bs_chart)

        y=list(df_bs_filtered.columns)
        draw_chart(df_bs_chart ,y)

        st.write("### Balance Sheet")
        if not df_raw.empty:
            st.dataframe(df_raw, )
        else:
            st.warning("データが取得できませんでした")

    with tab3:
        period_choice = st.radio("C/F Period Select", ["Annual (年次)", "Quarterly (四半期)"], horizontal=True)
        if period_choice == "Annual (年次)":
            df_raw = stock['cashflow']
            title_suffix = "(Annual)"
        else:
            df_raw = stock['quarterly_cashflow']
            title_suffix = "(Quarterly)"
        cf_mapping = {
            "Operating Cash Flow": ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities", "Total Cash From Operating Activities"],
            "Investing Cash Flow": ["Investing Cash Flow", "Cash Flow From Continuing Investing Activities", "Total Cash Flows From Investing Activities"],
            "Financing Cash Flow": ["Financing Cash Flow", "Cash Flow From Continuing Financing Activities", "Total Cash Flows From Financing Activities"],
            "Free Cash Flow": ["Free Cash Flow", "Repurchase Of Capital Stock"] # 稀に無ければ営業+投資で自作も可能ですが通常yfinanceにあります
        }
        df_filtered = pd.DataFrame(index=df_raw.columns) # 1. 元データ（df_raw）と同じ「日付インデックス」を持つ、空のDataFrameを先に作る
        for custom_name, yf_keys in cf_mapping.items(): # 2. 安全に名寄せしてデータを格納していく
            for key in yf_keys:
                if key in df_raw.index:
                    df_filtered[custom_name] = df_raw.loc[key] # 元のデータを転置（T）の形で、インデックス（日付）を一致させて格納
                    break
        df_chart = df_filtered.copy() 
        df_chart.index = index_is(period_choice, df_chart)

        y=list(df_filtered.columns)
        draw_chart(df_chart, y)

        st.write("### Cash Flow")

        if not df_raw.empty:
            st.dataframe(df_raw)
        else:
            st.warning("データが取得できませんでした")
else:
    st.error("TICKER_MAP が読み込まれていません。Mainページから起動してください。")

