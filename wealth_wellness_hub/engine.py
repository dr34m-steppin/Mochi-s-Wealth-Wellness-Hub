from __future__ import annotations

from copy import deepcopy
from statistics import mean
from typing import Dict, List

DEFAULT_HOLDINGS: List[Dict] = [
    {"name": "Savings Account", "class": "Cash", "value": 42000, "liquidity_days": 1, "volatility": 0.01},
    {"name": "Global Equity ETF", "class": "Public Equities", "value": 86000, "liquidity_days": 2, "volatility": 0.19},
    {"name": "SG Bond Fund", "class": "Fixed Income", "value": 35000, "liquidity_days": 2, "volatility": 0.06},
    {"name": "Rental Condo Share", "class": "Private Assets", "value": 65000, "liquidity_days": 120, "volatility": 0.09},
    {"name": "BTC + ETH Wallet", "class": "Digital Assets", "value": 28000, "liquidity_days": 1, "volatility": 0.62},
    {"name": "Angel Syndicate", "class": "Alternatives", "value": 18000, "liquidity_days": 365, "volatility": 0.35},
]

BEHAVIOR_HISTORY = {
    "monthly_contribution_consistency": [1, 1, 0.9, 1, 0.8, 1, 0.95, 1, 0.85, 1, 1, 0.92],
    "panic_sell_events_last_12m": 1,
    "rebalancing_actions_last_12m": 4,
}

HEALTH_TIMELINE = [
    {"month": "Apr", "score": 61},
    {"month": "May", "score": 63},
    {"month": "Jun", "score": 66},
    {"month": "Jul", "score": 64},
    {"month": "Aug", "score": 68},
    {"month": "Sep", "score": 70},
    {"month": "Oct", "score": 72},
    {"month": "Nov", "score": 73},
    {"month": "Dec", "score": 71},
    {"month": "Jan", "score": 75},
    {"month": "Feb", "score": 77},
    {"month": "Mar", "score": 79},
]


def _total_value(holdings: List[Dict]) -> float:
    return sum(item["value"] for item in holdings)


def _allocation_by_class(holdings: List[Dict]) -> List[Dict]:
    total = _total_value(holdings)
    buckets: Dict[str, float] = {}
    for h in holdings:
        buckets[h["class"]] = buckets.get(h["class"], 0) + h["value"]
    return [
        {"class": k, "value": v, "weight": round((v / total) * 100, 2) if total else 0}
        for k, v in sorted(buckets.items(), key=lambda x: x[1], reverse=True)
    ]


def _diversification_score(alloc: List[Dict]) -> float:
    hhi = sum((row["weight"] / 100.0) ** 2 for row in alloc)
    n = max(len(alloc), 1)
    min_hhi = 1.0 / n
    raw = 1 - ((hhi - min_hhi) / (1 - min_hhi)) if n > 1 else 0
    return max(0.0, min(100.0, raw * 100))


def _liquidity_score(holdings: List[Dict], monthly_burn: float = 3500.0) -> float:
    total = _total_value(holdings)
    liquid_7d = sum(h["value"] for h in holdings if h["liquidity_days"] <= 7)
    cash_only = sum(h["value"] for h in holdings if h["class"] == "Cash")

    liquid_mix_score = (liquid_7d / total) * 100 if total > 0 else 0
    emergency_months = cash_only / monthly_burn if monthly_burn > 0 else 0
    emergency_score = min(100.0, (emergency_months / 6.0) * 100)

    return max(0.0, min(100.0, liquid_mix_score * 0.7 + emergency_score * 0.3))


def _behavioral_resilience_score() -> float:
    consistency = mean(BEHAVIOR_HISTORY["monthly_contribution_consistency"]) * 100
    panic_penalty = BEHAVIOR_HISTORY["panic_sell_events_last_12m"] * 12
    rebalance_bonus = min(8, BEHAVIOR_HISTORY["rebalancing_actions_last_12m"] * 1.5)
    score = consistency * 0.85 - panic_penalty + rebalance_bonus
    return max(0.0, min(100.0, score))


def _risk_heat(holdings: List[Dict]) -> float:
    total = _total_value(holdings)
    if total == 0:
        return 0
    weighted_vol = sum((h["value"] / total) * h["volatility"] for h in holdings)
    return round(min(100.0, weighted_vol * 100 * 1.6), 2)


def _wellness_score(div_score: float, liq_score: float, beh_score: float) -> float:
    return round(div_score * 0.4 + liq_score * 0.35 + beh_score * 0.25, 2)


def _recommendations(overview: Dict, allocation: List[Dict], emergency_target: int) -> List[Dict]:
    recs = []

    digital_weight = next((x["weight"] for x in allocation if x["class"] == "Digital Assets"), 0)
    private_weight = next((x["weight"] for x in allocation if x["class"] == "Private Assets"), 0)

    if overview["metrics"]["liquidity"] < 82:
        recs.append({
            "title": "Increase liquidity runway",
            "impact": "+6 to +11 Wellness Score",
            "action": f"Auto-route 25% of monthly inflows to cash-like funds until {emergency_target} months of expenses is reached.",
        })
    if overview["metrics"]["diversification"] < 78:
        recs.append({
            "title": "Reduce concentration risk",
            "impact": "+4 to +8 Wellness Score",
            "action": "Shift 8-12% from concentrated sleeves into diversified global multi-asset exposure.",
        })
    if digital_weight > 9:
        recs.append({
            "title": "Stabilize digital sleeve volatility",
            "impact": "Drawdown risk down ~14%",
            "action": "Cap speculative tokens and blend with tokenized money-market instruments.",
        })
    if private_weight > 20:
        recs.append({
            "title": "Improve private asset optionality",
            "impact": "Liquidity stress reduced",
            "action": "Add a secondary-market exit plan and track expected settlement windows.",
        })

    recs.append({
        "title": "Behavioral nudge automation",
        "impact": "Consistency up to 95%+",
        "action": "Enable rule-based monthly investing and drawdown alerts before emotional decisions.",
    })
    recs.append({
        "title": "Goal-linked smart buckets",
        "impact": "Clearer client-adviser alignment",
        "action": "Segment assets into safety, growth, and optionality buckets with explicit target ranges.",
    })

    return recs[:4]


def build_dashboard_snapshot(holdings: List[Dict] | None = None, emergency_target: int = 6) -> Dict:
    base = deepcopy(holdings if holdings is not None else DEFAULT_HOLDINGS)
    total = _total_value(base)
    allocation = _allocation_by_class(base)

    metrics = {
        "diversification": round(_diversification_score(allocation), 2),
        "liquidity": round(_liquidity_score(base), 2),
        "behavioral_resilience": round(_behavioral_resilience_score(), 2),
    }
    risk_heat = _risk_heat(base)
    wellness = _wellness_score(
        metrics["diversification"],
        metrics["liquidity"],
        metrics["behavioral_resilience"],
    )

    overview = {
        "total_net_worth": round(total, 2),
        "wellness_score": wellness,
        "risk_heat": risk_heat,
        "metrics": metrics,
    }

    return {
        "overview": overview,
        "allocation": allocation,
        "timeline": HEALTH_TIMELINE,
        "holdings": base,
        "recommendations": _recommendations(overview, allocation, emergency_target),
    }


def run_scenario(equity_shock_pct: float, crypto_shock_pct: float, monthly_contribution: float, emergency_target: int):
    updated = deepcopy(DEFAULT_HOLDINGS)

    for h in updated:
        if h["class"] == "Public Equities":
            h["value"] = round(h["value"] * (1 + equity_shock_pct / 100.0), 2)
        elif h["class"] == "Digital Assets":
            h["value"] = round(h["value"] * (1 + crypto_shock_pct / 100.0), 2)

    cash_boost = round(monthly_contribution * 6, 2)
    for h in updated:
        if h["class"] == "Cash":
            h["value"] += cash_boost
            break

    snapshot = build_dashboard_snapshot(updated, emergency_target)
    snapshot["scenario"] = {
        "equity_shock_pct": equity_shock_pct,
        "crypto_shock_pct": crypto_shock_pct,
        "monthly_contribution": monthly_contribution,
        "emergency_target": emergency_target,
        "note": "Scenario assumes a 6-month horizon and immediate rebucketing of new contributions into cash buffer.",
    }
    return snapshot
