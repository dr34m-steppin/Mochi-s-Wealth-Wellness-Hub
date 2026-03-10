from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
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

MORTGAGE_BALANCE = 780000.0
BASE_MORTGAGE_PAYMENT = 4200.0
MONTHLY_EXPENSE_BASE = 7200.0


def _total_value(holdings: List[Dict]) -> float:
    return sum(item["value"] for item in holdings)


def _scale_holdings_to_net_worth(holdings: List[Dict], target_total: float | None) -> List[Dict]:
    if target_total is None:
        return deepcopy(holdings)
    current_total = _total_value(holdings)
    if current_total <= 0:
        return deepcopy(holdings)
    ratio = target_total / current_total
    scaled = deepcopy(holdings)
    for holding in scaled:
        holding["value"] = round(holding["value"] * ratio, 2)
    return scaled


def scale_holdings_to_net_worth(holdings: List[Dict], target_total: float | None) -> List[Dict]:
    return _scale_holdings_to_net_worth(holdings, target_total)


def serialize_holdings(holdings: List[Dict]) -> str:
    return json.dumps(holdings)


def normalize_holdings(holdings: List[Dict] | None) -> List[Dict]:
    if not holdings:
        return deepcopy(DEFAULT_HOLDINGS)
    normalized: List[Dict] = []
    for holding in holdings:
        normalized.append(
            {
                "name": str(holding["name"]),
                "class": str(holding["class"]),
                "value": round(float(holding["value"]), 2),
                "liquidity_days": int(holding["liquidity_days"]),
                "volatility": float(holding["volatility"]),
            }
        )
    return normalized


def deserialize_holdings(holdings_json: str | None) -> List[Dict] | None:
    if not holdings_json:
        return None
    try:
        parsed = json.loads(holdings_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list):
        return None
    return normalize_holdings(parsed)


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


def _liquid_net_worth(holdings: List[Dict]) -> float:
    return sum(h["value"] for h in holdings if h["liquidity_days"] <= 7)


def _behavioral_client_score() -> Dict:
    base_score = _behavioral_resilience_score()
    minute = datetime.utcnow().minute
    fluctuation = ((minute % 7) - 3) * 1.9
    current_score = int(max(35, min(92, round(base_score - 13 + fluctuation))))
    risk_band = (
        "High Risk of Emotional Trading"
        if current_score < 70
        else "Moderate Risk of Emotional Trading"
        if current_score < 82
        else "Disciplined Under Stress"
    )
    return {
        "score": current_score,
        "risk_label": risk_band,
        "summary": f"Current Client Score: {current_score}/100 - {risk_band}",
    }


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


def build_dashboard_snapshot_for_net_worth(total_net_worth: float | None, emergency_target: int = 6) -> Dict:
    scaled_holdings = _scale_holdings_to_net_worth(DEFAULT_HOLDINGS, total_net_worth)
    return build_dashboard_snapshot(scaled_holdings, emergency_target)


def build_dashboard_snapshot_for_client(holdings: List[Dict] | None, total_net_worth: float | None, emergency_target: int = 6) -> Dict:
    if holdings:
        return build_dashboard_snapshot(normalize_holdings(holdings), emergency_target)
    return build_dashboard_snapshot_for_net_worth(total_net_worth, emergency_target)


def build_behavioral_snapshot() -> Dict:
    client_score = _behavioral_client_score()
    return {
        "behavioral_drag_pct": 1.4,
        "value_lost_annual": 4600,
        "panic_sell_risk": 64,
        "discipline_score": 78,
        "intervention_readiness": 91,
        "adviser_visibility": 88,
        "client_score": client_score,
        "watchlist_flags": [
            {
                "title": "Drawdown Sensitivity",
                "status": "Elevated",
                "detail": "Client behavior suggests a higher chance of reactive selling after a sharp 10-15% portfolio drawdown.",
            },
            {
                "title": "Nudge Readiness",
                "status": "High",
                "detail": "The account is suitable for pre-commitment nudges, auto-rebalance prompts, and cooling-off alerts.",
            },
            {
                "title": "Adviser Actionability",
                "status": "Live",
                "detail": "Advisers can see rising emotional risk before an instruction to liquidate is placed.",
            },
        ],
        "protection_steps": [
            "Measure contribution consistency, panic-sell history, and rebalance discipline.",
            "Predict emotional selling risk from stress patterns and concentration pressure.",
            "Trigger pre-loss nudges before reactive sell behavior appears.",
            "Surface adviser alerts when a client enters a high-emotion window.",
        ],
    }


def evaluate_trade_intervention(asset_name: str, trade_amount: float, unrealized_loss_pct: float) -> Dict:
    liquid_net_worth = _liquid_net_worth(DEFAULT_HOLDINGS)
    client_score = _behavioral_client_score()
    exceeds_size_limit = trade_amount > liquid_net_worth * 0.05
    low_behavioral_score = client_score["score"] < 70
    trigger = exceeds_size_limit and low_behavioral_score

    return {
        "triggered": trigger,
        "checks": {
            "trade_size_pct_liquid_net_worth": round((trade_amount / liquid_net_worth) * 100, 2) if liquid_net_worth else 0,
            "exceeds_size_limit": exceeds_size_limit,
            "behavioral_score": client_score["score"],
            "below_behavioral_threshold": low_behavioral_score,
        },
        "stage_one": {
            "message": (
                f"Market Volatility Alert. You are about to liquidate at a {unrealized_loss_pct:.0f}% loss. "
                "Historically, portfolios structured like yours recover within 14 months. "
                "Are you sure you want to lock in this loss?"
            ),
            "buttons": ["Cancel Trade", "Proceed Anyway"],
        },
        "stage_two": {
            "message": (
                "Per your Wealth Protection Agreement, high-volume trades during severe market drawdowns "
                "require a 24-hour cooldown period."
            ),
            "countdown_seconds": 24 * 60 * 60,
            "cancel_available": True,
        },
        "stage_three": {
            "adviser_alert": (
                f"Client X attempted to panic sell SGD {trade_amount:,.0f} of {asset_name}. "
                "Trade is currently locked in a 24-hour cooldown. Recommended action: "
                "Call client to discuss intergenerational wealth continuity and long-term goals."
            ),
            "email_status": "queued-for-adviser-review",
        },
    }


def run_stress_test(rate_hike_pct: float, market_crash_pct: float, income_loss_months: int) -> Dict:
    liquid_cash = next(h["value"] for h in DEFAULT_HOLDINGS if h["class"] == "Cash")
    mortgage_payment = BASE_MORTGAGE_PAYMENT + (rate_hike_pct * 420)
    equity_value = sum(h["value"] for h in DEFAULT_HOLDINGS if h["class"] == "Public Equities")
    post_crash_equity_value = equity_value * (1 + market_crash_pct / 100.0)
    monthly_cash_burn = MONTHLY_EXPENSE_BASE + mortgage_payment
    if income_loss_months > 0:
        monthly_cash_burn += 900
    buffer_months = liquid_cash / monthly_cash_burn if monthly_cash_burn else 0

    return {
        "inputs": {
            "rate_hike_pct": rate_hike_pct,
            "market_crash_pct": market_crash_pct,
            "income_loss_months": income_loss_months,
        },
        "outputs": {
            "mortgage_payment": round(mortgage_payment, 2),
            "post_crash_equity_value": round(post_crash_equity_value, 2),
            "monthly_cash_burn": round(monthly_cash_burn, 2),
            "buffer_months": round(buffer_months, 1),
            "message": (
                f"Stress Test Result: At a +{rate_hike_pct:.1f}% rate hike and {income_loss_months} months "
                f"without income, your liquid cash will be depleted in {buffer_months:.1f} months."
            ),
            "recommendation": (
                "Reallocate 5% of your Equities into high-yield Cash Deposits to build a safer buffer."
                if buffer_months < income_loss_months
                else "Your current cash buffer is resilient, but a modest rebalance toward deposits would improve optionality."
            ),
        },
        "liabilities": {
            "mortgage_balance": MORTGAGE_BALANCE,
        },
    }


def run_scenario(
    equity_shock_pct: float,
    crypto_shock_pct: float,
    monthly_contribution: float,
    emergency_target: int,
    total_net_worth: float | None = None,
):
    updated = _scale_holdings_to_net_worth(DEFAULT_HOLDINGS, total_net_worth)

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
