from pydantic import BaseModel, Field


class ScenarioInput(BaseModel):
    equity_shock_pct: float = Field(default=-8.0, ge=-80, le=80)
    crypto_shock_pct: float = Field(default=-18.0, ge=-90, le=120)
    monthly_contribution: float = Field(default=1200.0, ge=0, le=20000)
    emergency_buffer_target_months: int = Field(default=6, ge=1, le=24)


class TradeInterventionInput(BaseModel):
    asset_name: str = Field(default="S&P500 ETF", min_length=2, max_length=80)
    trade_amount: float = Field(default=500000.0, gt=0, le=5000000)
    unrealized_loss_pct: float = Field(default=15.0, ge=0, le=100)


class StressTestInput(BaseModel):
    rate_hike_pct: float = Field(default=3.0, ge=0, le=4)
    market_crash_pct: float = Field(default=-20.0, ge=-40, le=0)
    income_loss_months: int = Field(default=6, ge=0, le=24)


class NetWorthInput(BaseModel):
    total_net_worth: float = Field(default=274000.0, gt=1000, le=100000000)


class HoldingInput(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    class_name: str = Field(alias="class", min_length=2, max_length=80)
    value: float = Field(ge=0, le=100000000)
    liquidity_days: int = Field(ge=0, le=3650)
    volatility: float = Field(ge=0, le=5)

    model_config = {"populate_by_name": True}


class HoldingsInput(BaseModel):
    holdings: list[HoldingInput]
