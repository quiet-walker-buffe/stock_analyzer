import streamlit as st
import pandas as pd
import plotly.express as px  # 💡 Web用の動くグラフを作るための最強ライブラリ
from data.download import load_local_data
from utils import show_common_sidebar

def calculate_correlation_from_local(tickers):
    # 各銘柄の「株価シリーズ」をストックしていくための辞書
    price_dict = {}
    
    for t in tickers:
        # 1. ローカルから辞書データをロード
        local_data = load_local_data(t)
        
        # 2. 辞書の中から「history（DataFrame）」を取り出す
        history_df = local_data["history"]
        
        # 3. historyの中から「Close（終値）」列だけを引っこ抜く
        # ※yfinanceのバージョンによっては 'Close' または 'Adj Close'
        if 'Close' in history_df.columns:
            # 💡 後で連結したときに誰の株価か分かるよう、列名をティッカー名に変更します
            price_dict[t] = history_df['Close']
        elif 'Adj Close' in history_df.columns:
            price_dict[t] = history_df['Adj Close']

    # ─── 💡 ここが最大のポイント！ ───
    # 集めた複数の株価データを、共通の「Date（日付）」を軸にして、横（列方向）にガッチャンコします
    # axis=1 は「横に並べる」という意味です。日付がズレていてもPandasが自動で綺麗に整列させてくれます
    combined_df = pd.concat(price_dict, axis=1)
    # 1. 日付のタイムゾーン情報を完全に消去して「ただの日付」に統一する
    combined_df.index = combined_df.index.tz_localize(None)
    
    # 2. 土日祝日や時差で「片方しかデータがない日」の空欄（NaN）を、
    #    「前日の株価（一晩前の終値）」をスライドさせて無理やり埋める（Forward Fill）
    combined_df = combined_df.ffill()
    
    # 3. データの最初の方など、どうしても埋まらない部分（bfill）を処理
    combined_df = combined_df.bfill()
    # 4. これで完璧な1枚の表になったので、相関係数を計算
    correlation_matrix = combined_df.corr()
    
    return correlation_matrix


selected_ticker = None
selected_ticker = show_common_sidebar()

if selected_ticker is None:
    st.warning("⚠️ セッションの有効期限が切れました。")
    st.info("サイドバーの「銘柄検索」から再度銘柄を選択してください。自動的に分析が再開されます。")
    st.stop()

st.title("📊 ポートフォリオ相関性分析 (All-Weather Style)")
st.write("過去の時系列データから、銘柄同士の値動きの連動性を可視化します。")

# ─── 💡 1. 以前作成した関数でマトリクスを取得 ───
my_portfolio = st.session_state.history
matrix = calculate_correlation_from_local(my_portfolio)

# ─── 💡 2. Plotlyでインタラクティブなヒートマップを作成 ───
fig = px.imshow(
    matrix,
    text_auto=".2f",                # 💡 マトリクスの中に数値を小数点2桁で自動表示
    aspect="auto",                  # グラフの縦横比を自動調整
    color_continuous_scale="RdBu_r", # 💡 レイ・ダリオ風の「赤（高相関）〜青（低相関）」のカラーパレット
    labels=dict(color="相関係数"),   # カラーバーのラベル名
    zmin=-1,                        # 最小値
    zmax=1                          # 最大値
)

# ─── 💡 3. グラフのデザイン（レイアウト）を微調整 ───
fig.update_layout(
    title_text="銘柄間 相関係数マトリクス",
    title_x=0.5,                    # タイトルを中央寄せ
    width=600,                      # グラフの幅
    height=500                      # グラフの高さ
)

# ─── 💡 4. Streamlit画面に出力！ ───
# st.pyplot ではなく st.plotly_chart を使います
st.plotly_chart(fig, width='stretch')

st.caption("※ 1.0に近い（赤い）ほど同じ動きをし、0に近い（白い）ほどバラバラに動く（分散投資が効いている）ことを示します。")