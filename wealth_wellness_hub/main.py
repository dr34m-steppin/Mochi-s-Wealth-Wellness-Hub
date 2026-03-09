from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from wealth_wellness_hub.engine import build_dashboard_snapshot, run_scenario
from wealth_wellness_hub.models import ScenarioInput

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Mochi Wealth Wellness Hub")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/dashboard")
def dashboard_data():
    return build_dashboard_snapshot()


@app.post("/api/scenario")
def scenario_data(payload: ScenarioInput):
    return run_scenario(
        equity_shock_pct=payload.equity_shock_pct,
        crypto_shock_pct=payload.crypto_shock_pct,
        monthly_contribution=payload.monthly_contribution,
        emergency_target=payload.emergency_buffer_target_months,
    )
