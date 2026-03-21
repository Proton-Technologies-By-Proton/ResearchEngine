from pytrends.request import TrendReq


def fetch_trends_data(query):
    try:
        pytrends = TrendReq(hl='en-IN', tz=330)

        pytrends.build_payload([query], timeframe='today 3-m')

        data = pytrends.interest_over_time()

        if data.empty:
            return {"trend_score": 0, "direction": "No Data"}

        if "isPartial" in data.columns:
            data = data.drop(columns=["isPartial"])

        values = data[query].tolist()

        avg = sum(values) / len(values)

        if values[-1] > values[0]:
            direction = "Rising"
        elif values[-1] < values[0]:
            direction = "Falling"
        else:
            direction = "Stable"

        return {
            "trend_score": round(avg, 2),
            "direction": direction
        }

    except:
        return {"trend_score": 0, "direction": "Error"}