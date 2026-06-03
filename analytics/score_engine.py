def compute_signal_score(data: dict) -> float:
    score = 0

    score += abs(data["pct_change"])
    score += data["rvol"] * 2

    return score

def calculate_metric_score(value, factor, min_limit=0, max_limit=10):
    """
    値を係数で割り、0〜10点の範囲に収める関数
    """
    if value and factor :
        raw = value / factor
    else:
        return None
    return max(float(min_limit), min(float(max_limit), float(raw)))

def calculate_quority_score(data: dict) -> float:
    """
スコアリング・ロジック 9項目（各10点）で組む場合の簡易基準案
カテゴリ    項目                10点の基準（例）
収益性
            FCF Yield           7.0% 以上
            FCF Margin          25% 以上
            OCF / Net Income    1.2 以上（利益より現金が多い）
            Gross Margin        60% 以上（圧倒的ブランド/技術）
成長性
            Def. Rev Growth     売上成長率 + 5% 以上
            Revenue Growth      20% 以上（または業種平均以上）
            R&D / Revenue       15% 以上（未来への投資が旺盛）
健全性
            Net Debt / EBITDA   0%（無借金）で 5点、10%以上（超キャッシュリッチ）で 10点
            Equity Ratio        70% 以上（要塞級）
    """
    score1 = calculate_metric_score(data['revenue_growth'] , 0.02)
    score2 = calculate_metric_score(data['gross_margin'] , 0.06)
    score3 = calculate_metric_score(data['rd_ratio'] , 0.015)
    score4 = calculate_metric_score(data['equity_ratio'] , 0.07)
    score5 = calculate_metric_score((data['def_rev_growth'] - data['revenue_growth']) , 0.005)
    score6 = calculate_metric_score(- (data['net_debt'] / data['market_cap']) , 0.02, -5.0, 5.0) + 5.0
    score7 = calculate_metric_score(data['operating_cf'] , data['net_income'], 0.0012)
    score8 = calculate_metric_score(data['fcf_margin'] , 0.025)
    score9 = calculate_metric_score(data['fcf_yield'] , 0.007)
      
    if all(s is not None for s in [score1, score2, score3, score4, score5, score6, score7, score8, score9]):
        total = score1 + score2 + score3 + score4 + score5 + score6 + score7 + score8 + score9
    else:
        total = None
    return {
        'ticker': data['ticker'],
        'Revenue Growth': score1, #P/L 易
        'Gross Margin': score2, #P/L 中
        'R&D / Revenue': score3, #P/L 難
        'Equity Ratio': score4, #B/S 易
        'Def. Rev Growth': score5, #B/S 中
        'Net Cash Ratio': score6, #B/S 難
        'OCF / Net Income': score7, #C/F 易
        'FCF Margin': score8, #C/F 中
        'FCF Yield': score9, #C/F 難
        'total score': total
    }
