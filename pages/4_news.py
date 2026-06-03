import yfinance as ticker_context
import streamlit as st
from utils import show_common_sidebar
from services.ai_service import call_gemini
from utils import get_url

def get_latest_editorial_text(ticker_symbol):
    """yfinanceから最新のニューステキストを安全に取得する関数"""
    company = ticker_context.Ticker(ticker_symbol)
    combined_text = ""
    
    try:
        news = company.news
        if not news:
            return "ニュースデータが空でした。"
            
        for i, item in enumerate(news):
            content_data = item.get('content', {})
            title = content_data.get('title', 'タイトルなし')
            summary = content_data.get('summary') or content_data.get('description') or '詳細テキストなし'
            combined_text += f"\n【ニュース {i+1}】\nタイトル: {title}\n内容: {summary}\n"
        
        return combined_text
        
    except Exception as e:
        return f"テキスト取得エラー: {e}"

def analyze_investment_risk(text_data):
    """取得した長文テキストを Gemini 3.1 Flash Lite に投げて投資分析させる関数"""
    print("\n🤖 Gemini 3.1 Flash Lite がテキストを分析中...")
    
    prompt = f"""
    以下の英文は、対象銘柄に関する直近のニュース・市場の関心事のテキストです。
    Copilotなどの一般的なニュース要約とは異なり、「投資判断におけるリスク、または今後のボラティリティの要因」に特化して
    200文字程度で簡潔に分析してください。

    特に、入力されたデータから読み取れる以下の点について、日本語でプロの投資家目線で簡潔に教えてください。
    1. 現在、市場やメディアがこの銘柄に対して最も警戒・注目している材料は何か
    2. ニュースの文脈から読み取れる、中長期的なポジティブ要因とネガティブな懸念点
    3. 総括：今この銘柄に向き合うにあたって、投資家が注意すべきボラティリティ（株価乱高下）の火種

    【ニュースデータ】
    {text_data}
    """

    return prompt


selected_ticker = None
selected_ticker = show_common_sidebar()

if selected_ticker is None:
    st.warning("⚠️ セッションの有効期限が切れました。")
    st.info("サイドバーの「銘柄検索」から再度銘柄を選択してください。自動的に分析が再開されます。")
    st.stop()
    
raw_news_text = get_latest_editorial_text(selected_ticker)
st.write(raw_news_text)
if st.button(f"{selected_ticker} :上記newsについてAI診断する"):
    with st.spinner("Geminiが財務諸表を読み解いています..."):  
        
        if "エラー" not in raw_news_text: # 2. 取得成功していればGeminiへ渡す
            prompt = analyze_investment_risk(raw_news_text)
            ai_analysis = call_gemini(prompt)
            st.info(ai_analysis)
            print(ai_analysis)
        else:
            st.write(raw_news_text)


if selected_ticker:
    ir_url = get_url(selected_ticker)
    
    st.subheader(f"🏢 {selected_ticker} 一次ソース・リサーチ")
    st.link_button(
        label=f"👉 {selected_ticker} 公式IR（決算短信・10-Q）を開く", 
        url=ir_url
    )
    
    st.caption("※公式IRページが開いたら、最新の「10-Q」や「Press Release」のPDFをブラウザのCopilot等に読み込ませて詳細をチェックしてください。")
