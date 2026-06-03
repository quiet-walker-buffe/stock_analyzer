MAG7 = ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA"]

AI = [
    "NVDA","MSFT","GOOGL","AMZN",
    "AVGO","AMD","TSM","ASML",
    "PLTR","SMCI"
]

BUFFETT = ["BRK-B","KO","OXY","AXP","MCO"]

CORE = list(set(MAG7 + AI + BUFFETT))

SP500 = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META",
    "GOOGL", "GOOG", "BRK-B", "LLY", "AVGO",
    "TSLA", "JPM", "XOM", "UNH", "V",
    "MA", "HD", "PG", "COST", "MRK", "^GSPC"
]

RISK_SAMPLE = ["NVDA", "MSFT", "GOOGL", "AMD", "TSM", "AAPL", "AMZN", "QQQ", "GLD", "TLT"]

JAPAN = ["7201.T", "7203.T", "9984.T", "8001.T", "8002.T", "8031.T", "8053.T", "8058.T"]

TECH_GROWTH = [
    "NVDA", "MSFT", "ADBE", "CRM", "SNPS", 
    "CDNS", "AVGO", "PANW", "NOW", "INTU"
]

CASH_MACHINE = [
    "AAPL", "GOOGL", "META", "V", "MA", 
    "ACN", "ORCL", "BKNG", "CSCO", "TXN"
]

HEALTHCARE = [
    "UNH", "LLY", "ABBV", "ISRG", "SYK", 
    "TMO", "DHR", "VRTX", "REGN", "ZTS"
]

BRAND_POWER = [
    "COST", "MSCI", "SPGI", "MCO", "MAR", 
    "SBUX", "NKE", "TJX", "LULU", "CMG"
]

ENERGY = [
    "GE", "CAT", "DE", "LMT", "WM", 
    "RSG", "LIN", "EOG", "COP", "PH"
]

ALL_TARGET = (
    TECH_GROWTH + 
    CASH_MACHINE + 
    HEALTHCARE + 
    BRAND_POWER + 
    ENERGY
)