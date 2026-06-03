from datetime import datetime
import pytz
US_TZ = pytz.timezone("US/Eastern")

def classify_volume_spike(rvol: float) -> str:
    if rvol >= 3:
        return "EXTREME"
    elif rvol >= 2:
        return "HIGH"
    elif rvol >= 1.5:
        return "ELEVATED"
    else:
        return "NORMAL"
    
def detect_52w_levels(stock, current_price: float): #テクニカル　不使用
    hist_1y = stock.history(period="1y")

    if hist_1y.empty:
        return False, None, False, None

    high_52w = hist_1y["High"].max()
    low_52w = hist_1y["Low"].min()

    near_high = current_price / high_52w >= 0.97
    near_low = current_price / low_52w <= 1.03

    return near_high, high_52w, near_low, low_52w

def detect_breakout(pct_change: float, rvol: float) -> str: #テクニカル　不使用
    direction = "BULL" if pct_change > 0 else "BEAR"

    if abs(pct_change) >= 4 and rvol >= 3:
        return f"STRONG_{direction}_BREAKOUT"
    elif abs(pct_change) >= 2 and rvol >= 2:
        return f"{direction}_BREAKOUT"
    else:
        return "NONE"

def detect_market_regime(data):

    score = 0

    spy = data["S&P 500"]["change"]
    vix = data["VIX"]["change"]
    dxy = data["DXY"]["change"]
    rate = data["US10Y"]["change"]

    score += 1 if spy > 0 else -1
    score += 1 if vix < 0 else -1
    score += 1 if dxy < 0 else -1
    score -= 1 if rate > 0 else -1

    if score >= 2:
        regime = "RISK ON"
    elif score <= -2:
        regime = "RISK OFF"
    else:
        regime = "NEUTRAL"

    return score, regime

def detect_market_session():
    now = datetime.now(US_TZ)
    hour = now.hour
    minute = now.minute
    time = hour * 60 + minute

    # US market times (Eastern Time)
    pre_start = 4 * 60
    regular_start = 9 * 60 + 30
    regular_end = 16 * 60
    after_end = 20 * 60

    if pre_start <= time < regular_start:
        return "PRE"
    elif regular_start <= time < regular_end:
        return "REGULAR"
    elif regular_end <= time < after_end:
        return "AFTER"
    else:
        return "CLOSED"