import json
import streamlit as st
from data.fetch_data import load_ticker_map
from streamlit_local_storage import LocalStorage

TICKER_MAP = load_ticker_map()

def get_url(target_ticker):
    target_ticker = target_ticker.upper()
    
    target_rows = TICKER_MAP[TICKER_MAP['Ticker'] == target_ticker]
    if target_rows.empty:
        return []
    url = target_rows['Website'].values[0]
    return url

def get_competitors(target_ticker):

    target_ticker = target_ticker.upper()
    
    target_rows = TICKER_MAP[TICKER_MAP['Ticker'] == target_ticker]
    if target_rows.empty:
        return []
    target_industry = target_rows['Industry'].values[0]

    same_industry_df = TICKER_MAP[TICKER_MAP['Industry'] == target_industry]
    
    if target_ticker.endswith('.T'):
        competitors_df = same_industry_df[same_industry_df['Ticker'].str.endswith('.T', na=False)]
    else:
        competitors_df = same_industry_df[~same_industry_df['Ticker'].str.endswith('.T', na=False)]#チルダ:Pandasで「〜ではない（NOT）」の意味
        
    competitors = competitors_df['Ticker'].tolist()
    competitors = [c for c in competitors if c != target_ticker]
    
    return competitors

def on_pill_clicked():
    """pillsがクリックされた瞬間に、1回だけ裏で実行される関数"""
    selected = st.session_state.my_pill_selector # 現在クリックされた銘柄を一時的に変数に退避
    if not selected:
        return

    if st.session_state.get("delete_mode", False): # ── 🔥 ここでモード判定を行う ──
        if selected in st.session_state.history: # 【削除モードのとき】リストから消す
            st.session_state.history.remove(selected)
            st.toast(f"🗑️ {selected} を履歴から削除しました")
    else:
        reload_session_state(selected)
    st.session_state.my_pill_selector = None # 選択状態を「未選択（None）」に強制リセットする

def on_selectbox_clicked():
    selected = st.session_state.my_selectbox_selector
    if selected:
        reload_session_state(selected)

def reload_session_state(ticker): # 履歴に追加（重複を避け、最新が先頭に来るようにする）
    st.session_state.selected_ticker = ticker # メインのセレクトボックス側の記憶を選択された銘柄で上書き
    if ticker in st.session_state.history: 
        st.session_state.history.remove(ticker)
    st.session_state.history.insert(0, ticker)
    st.session_state.history = st.session_state.history[:10] # 履歴は直近5件程度に制限
    st.session_state["competitors"] = get_competitors(ticker) # competitors取得
    st.session_state["selected_sector"] = TICKER_MAP.loc[TICKER_MAP['Ticker'] == ticker, 'Sector'].values[0]
    st.session_state["selected_industry"] = TICKER_MAP.loc[TICKER_MAP['Ticker'] == ticker, 'Industry'].values[0]
    print(st.session_state["competitors"])
    print(st.session_state["selected_sector"])
    print(st.session_state["selected_industry"])
    
def show_common_sidebar():

    local_storage = LocalStorage()
        
    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = None
        st.session_state.history = []
        saved_history_json = []

        saved_history_json = local_storage.getItem("user_history") # ── 1. ブラウザから「JSON文字列」として履歴を読み出す ──

        if saved_history_json:
            try:
                st.session_state.history = json.loads(saved_history_json) # 文字列からリストに変換
                st.session_state.selected_ticker = st.session_state.history[0]
                if not isinstance(st.session_state.history, list): # 万が一リストの形をしていなかったら空リストにする
                    st.session_state.history = []
            except Exception:
                st.session_state.history = []
        else:
            st.session_state.history = []

    ticker_display_dict = {row['Ticker']: f"{row['Ticker']} | {row['LongName']}" for _, row in TICKER_MAP.iterrows()}
    options=list(ticker_display_dict.keys())
    st.sidebar.selectbox(
        "銘柄検索 (Ticker・半角入力)",
        options, #optionsには「Tickerのリスト」を渡し、表示だけ辞書を通す# ここは ['GOOGL', 'AAPL', ...]
        format_func=lambda x: ticker_display_dict.get(x), # 表示だけ書き換え
        index=None,
        placeholder="例: Google, NVDA...",
        key="my_selectbox_selector",
        on_change=on_selectbox_clicked,
    )

    st.sidebar.info(f"{st.session_state.selected_ticker}") 
    st.sidebar.subheader("🕒 最近チェックした銘柄") # ---履歴の表示---

    delete_mode = st.sidebar.toggle("🗑️ 削除モード", key="delete_mode")
    
    if delete_mode: # 見出しの文字をモードによって変えると親切です
        st.sidebar.caption("⚠️ クリックで履歴から消去")
    else:
        st.sidebar.caption("🐾 最近見た銘柄 (クリックで選択)")

    st.sidebar.pills(
        label="history_pills",
        options=st.session_state.history,
        label_visibility="collapsed",
        key="my_pill_selector",      # 💡 この中身を上で None に上書きしています
        on_change=on_pill_clicked    
    )

    if st.session_state.history:
        history_json = json.dumps(st.session_state.history)
        local_storage.setItem("user_history", history_json)

    return st.session_state.selected_ticker

