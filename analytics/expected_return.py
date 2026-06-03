def expected_return(data):

    growth = data.get("growth_rate", 0)

    dividend = data.get("dividend_yield", 0)

    per_now = data.get("per", None)
    per_avg = data.get("per_avg", None)

    valuation = 0

    if per_now and per_avg:
        valuation = (per_avg - per_now) / per_now / 5

    er = growth + dividend + valuation

    return er