from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from wealth_wellness_hub.db import get_connection, init_db
from wealth_wellness_hub.engine import build_dashboard_snapshot, run_scenario
from wealth_wellness_hub.models import ScenarioInput
from wealth_wellness_hub.security import hash_password, verify_password

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Mochi Wealth Wellness Hub")
app.add_middleware(SessionMiddleware, secret_key="swan-dev-secret-change-me")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.on_event("startup")
def startup() -> None:
    init_db()


def current_user_email(request: Request) -> str | None:
    return request.session.get("user_email")


def behavioral_insight_snapshot() -> dict:
    return {
        "behavioral_drag_pct": 1.4,
        "value_lost_annual": 4600,
        "panic_sell_risk": 64,
        "discipline_score": 78,
        "intervention_readiness": 91,
        "adviser_visibility": 88,
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


def render_auth(request: Request, mode: str, error: str = ""):
    return templates.TemplateResponse(
        "auth.html",
        {
            "request": request,
            "mode": mode,
            "error": error,
            "page_title": "SWAN Access",
            "card_title": "Welcome back" if mode == "login" else "Create your SWAN account",
            "card_note": "Sign in to view your protected dashboard." if mode == "login" else "Use your email to create an account and store access securely.",
            "form_action": "/login" if mode == "login" else "/signup",
            "submit_label": "Log In" if mode == "login" else "Create Account",
        },
    )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user_email = current_user_email(request)
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "user_email": user_email})


@app.get("/behavioral-protection", response_class=HTMLResponse)
def behavioral_protection_page(request: Request):
    user_email = current_user_email(request)
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(
        "behavioral_protection.html",
        {
            "request": request,
            "user_email": user_email,
            "insight": behavioral_insight_snapshot(),
        },
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if current_user_email(request):
        return RedirectResponse("/", status_code=303)
    return render_auth(request, "login")


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = get_connection()
    try:
        row = conn.execute("SELECT email, password_hash FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    finally:
        conn.close()

    if not row or not verify_password(password, row["password_hash"]):
        return render_auth(request, "login", "Invalid email or password.")

    request.session["user_email"] = row["email"]
    return RedirectResponse("/", status_code=303)


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    if current_user_email(request):
        return RedirectResponse("/", status_code=303)
    return render_auth(request, "signup")


@app.post("/signup", response_class=HTMLResponse)
def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    normalized_email = email.strip().lower()
    if password != confirm_password:
        return render_auth(request, "signup", "Passwords do not match.")
    if len(password) < 8:
        return render_auth(request, "signup", "Password must be at least 8 characters.")

    conn = get_connection()
    try:
        existing = conn.execute("SELECT 1 FROM users WHERE email = ?", (normalized_email,)).fetchone()
        if existing:
            return render_auth(request, "signup", "An account with this email already exists.")

        conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (normalized_email, hash_password(password)),
        )
        conn.commit()
    finally:
        conn.close()

    request.session["user_email"] = normalized_email
    return RedirectResponse("/", status_code=303)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/api/dashboard")
def dashboard_data(request: Request):
    if not current_user_email(request):
        return RedirectResponse("/login", status_code=303)
    return build_dashboard_snapshot()


@app.post("/api/scenario")
def scenario_data(request: Request, payload: ScenarioInput):
    if not current_user_email(request):
        return RedirectResponse("/login", status_code=303)
    return run_scenario(
        equity_shock_pct=payload.equity_shock_pct,
        crypto_shock_pct=payload.crypto_shock_pct,
        monthly_contribution=payload.monthly_contribution,
        emergency_target=payload.emergency_buffer_target_months,
    )
