def generate_full_insights(videos, trends, criteria, dynamic_keywords):
    insights = {
        "summary": [],
        "opportunity": "",
        "trends": "",
        "youtube": {}
    }

    if not videos:
        return insights

    # ===== KEYWORDS =====
    insights["summary"].append("TOP KEYWORDS:")

    for k, v in dynamic_keywords[:6]:
        insights["summary"].append(f"• {k}: {v}")

    # ===== TRENDS =====
    trend_score = trends.get("trend_score", 0)
    direction = trends.get("direction", "Unknown")

    insights["summary"].append("\nTREND ANALYSIS:")
    insights["summary"].append(f"• Score: {trend_score}")
    insights["summary"].append(f"• Direction: {direction}")

    # ===== OPPORTUNITY =====
    opp = []

    if dynamic_keywords:
        opp.append(f"High competition on '{dynamic_keywords[0][0]}'")

    if trend_score > 60:
        opp.append("High demand → Enter aggressively")

    if trend_score < 30:
        opp.append("Low demand → Be cautious")

    if direction == "Rising":
        opp.append("Trend rising → Early mover advantage")

    if len(dynamic_keywords) > 5:
        opp.append(f"Opportunity in '{dynamic_keywords[5][0]}'")

    insights["opportunity"] = "\n".join("• " + o for o in opp)

    insights["trends"] = f"{direction} ({trend_score})"
    insights["youtube"]["top_keywords"] = dynamic_keywords[:6]

    return insights