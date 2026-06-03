def get_market_signals(data):
    signals = []
    if data['fcf_growth_qoq'] > data['revenue_growth_qoq'] * 1.2:
        signals.append({"icon": "🚀", "label": "爆騰予兆", "desc": "収益性が劇的に向上しています qoq"})
    if data['fcf_growth_yoy'] > data['revenue_growth_yoy'] * 1.2:
        signals.append({"icon": "🚀", "label": "爆騰予兆", "desc": "収益性が劇的に向上しています yoy"})
    if data['cl_growth_qoq'] > 0.5:
        signals.append({"icon": "🔥", "label": "重要爆発", "desc": "客が行列を作っていますqoq"})
    if data['cl_growth_yoy'] > 0.5:
        signals.append({"icon": "🔥", "label": "重要爆発", "desc": "客が行列を作っていますyoy"})
    if (data['fcf'].iloc[0] > data['net_income'].iloc[0]) and (data['fcf_margin'].iloc[0] > 15.0):
        signals.append({"icon": "🔥", "label": "FCFの逆転", "desc": "投資回収のフェーズです"}) 
    if data['cl_ratio'].iloc[0] > data['cl_ratio'].iloc[1]:
        signals.append({"icon": "🔥", "label": "前受金倍率改善", "desc": "前受金倍率が改善しています"}) 
    if data['good_debt_ratio'].iloc[0] > 0.7:
        signals.append({"icon": "🔥", "label": "良い負債比率", "desc": "良い負債比率が70％overです"}) 
    if data['cl_growth_qoq'] > data['revenue_growth_qoq']:
        signals.append({"icon": "🔥", "label": "前受金の伸び", "desc": "前受金の伸びが、現在の売上成長率を上回っています"}) 
    if data['accrued_growth_yoy'] > 0.5:
        signals.append({"icon": "🔥", "label": "未払費用", "desc": "未払費用が前年比で50%以上増えています"}) 
    if data['gross_margin_ratio'].iloc[0] - data['gross_margin_ratio'].iloc[4] > 0.05:
        signals.append({"icon": "🔥", "label": "マージン拡大", "desc": "売上利益率が前年より5%以上増えています"}) 
    if data['accrued_growth_yoy'] and data['revenue_growth_qoq'] > 0.2:
        signals.append({"icon": "🔥", "label": "組織拡大の予兆", "desc": "将来の利益を見越した人材・リソース確保が加速しています"}) 
    return signals

def get_buffett_signals(data):
    signals = []
    if data['roe'] > 0.15 and data['pbr'] < 2.0:
        signals.append({"icon": "🐢", "label": "バフェット合格", "desc": "高い資本効率と割安性を両立"})
    if data['fcf'].iloc[0] / data['market_cap']> 0.07:
        signals.append({"icon": "🐢", "label": "バフェット合格", "desc": "FCF利回り (FCF / 時価総額) が 7% を超えています"})
    if (abs(data['dividend_payment'].iloc[0]) + abs(data['stock_buyback'].iloc[0])) / data['market_cap'] > data['bond_yield']:
        signals.append({"icon": "🐢", "label": "バフェット合格", "desc": "配当利回り + 自社株買い利回り が 米国債利回りを上回っています"})
    t_debt = data['total_debt'].iloc[0] if hasattr(data['total_debt'], 'iloc') else data['total_debt']
    if (t_debt - data['total_cash']) / data['ebitda'] < 3.0:
        signals.append({"icon": "🐢", "label": "バフェット合格", "desc": "Net Debt / EBITDA（借金が稼ぎに対して適正）が健全です"})
    if data['operating_cf'].iloc[0] / data['net_income'].iloc[0] > 1.0:
        signals.append({"icon": "🐢", "label": "バフェット合格", "desc": "「現金の質」が高い企業です"})
    return signals
