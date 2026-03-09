from pydantic import BaseModel, Field


class ScenarioInput(BaseModel):
    equity_shock_pct: float = Field(default=-8.0, ge=-80, le=80)
    crypto_shock_pct: float = Field(default=-18.0, ge=-90, le=120)
    monthly_contribution: float = Field(default=1200.0, ge=0, le=20000)
    emergency_buffer_target_months: int = Field(default=6, ge=1, le=24)
