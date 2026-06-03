from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import streamlit as st

load_dotenv(override=True)
CACHE = {}
GEMINI_MODEL = 'gemini-3.1-flash-lite'

def get_prompt(data):
    prompt = f"""
    あなたは百戦錬磨の個人投資家です。以下の
    銘柄: {data['ticker']} の財務スコアに基づき、「プロの視点」で分析してください。

    【スコア情報 (10点満点)】
        FCF Yield: {data['FCF Yield']}
        FCF Margin: {data['FCF Margin']}
        OCF / Net Income: {data['OCF / Net Income']}
        Gross Margin: {data['Gross Margin']}
        Def. Rev Growth: {data['Def. Rev Growth']}
        Revenue Growth: {data['Revenue Growth']}
        R&D / Revenue: {data['R&D / Revenue']}
        Net Cash Ratio: {data['Net Cash Ratio']}
        Equity Ratio: {data['Equity Ratio']}

    【出力形式】
    200文字程度で簡潔に。
    """
    return prompt

@st.cache_data(ttl=84000)  # 24時間有効
def call_gemini(prompt) -> str:
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=300,
            ),
            # タイムアウト等のHTTP設定は http_options で指定
            # SDKのバージョンにより config 内や Client 初期化時での指定が推奨される場合もあります
        )
        return response.text
    except Exception as e:
        st.error(f"AI診断でエラーが発生しました: {e}")
        return "診断をスキップします。"

def get_gemini_client():
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("コメント：GEMINI_API_KEY missing")

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    return client

