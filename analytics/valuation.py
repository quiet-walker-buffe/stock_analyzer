
def calculate_intrinsic_value(fcf, growth_rate, discount_rate=0.1, terminal_growth=0.02):
    """
    簡易版DCF: ゴードン・グロース・モデル
    discount_rate: 期待収益率（10%など）
    terminal_growth: 永続成長率（2%など）
    """
    next_fcf = fcf * (1 + growth_rate)
    intrinsic_value = next_fcf / (discount_rate - terminal_growth)
    return intrinsic_value