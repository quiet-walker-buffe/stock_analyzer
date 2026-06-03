def calc_growth(current, prior):
    """成長率を計算する（ゼロ除算対策付き）"""
    if prior is None or prior == 0:
        return 0.0
    return (current / prior) - 1.0

def get_growth_metrics(series):
    """Series（時系列データ）からQoQとYoYを一気に返す"""
    if len(series) < 5: # データが足りない場合
        return 0.0, 0.0
    
    qoq = calc_growth(series.iloc[0], series.iloc[1])
    yoy = calc_growth(series.iloc[0], series.iloc[4])
    return qoq, yoy