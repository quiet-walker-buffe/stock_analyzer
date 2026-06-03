
AI_GROWTH_MULTIPLIER = 1.10  # 調整可能



def apply_growth_modifier(ticker, base_score, ai_list):
    if ticker in ai_list:
        return round(base_score * AI_GROWTH_MULTIPLIER, 2)
    return base_score

def revenue_cagr(data, years=3):
    # data は load_local_data(ticker) で得た辞書
    try:
        financials = data.get('financials')
        if financials is None or "Total Revenue" not in financials.index:
            return None
            
        revenue = financials.loc["Total Revenue"]

        # データの件数チェック（pandasのシリーズなので iloc でアクセス）
        if len(revenue) < years + 1:
            return None

        # yfinanceのfinancialsは [0]が最新、[years]が過去
        end = revenue.iloc[0]
        start = revenue.iloc[years]

        if start <= 0: # マイナスやゼロ除算を防止
            return None

        cagr = (end / start) ** (1 / years) - 1
        return float(cagr)

    except Exception as e:
        # print(f"CAGR計算エラー: {e}")
        return None