# Mochi-s-Wealth-Wellness-Hub

A full-stack hackathon prototype for Problem Statement 1: Wealth Wellness Hub.

## What this solution does
- Unifies traditional, private, and digital assets into one Wealth Wallet view.
- Computes wellness metrics: diversification, liquidity, and behavioral resilience.
- Tracks historical health trend and risk concentration.
- Runs scenario simulations (market shocks + monthly contributions).
- Recommends personalized actions for clients and advisers.

## Tech stack
- Backend: FastAPI
- Frontend: HTML, CSS, vanilla JavaScript
- Runtime: Python 3.11+

## Windows setup (VSCode)
```powershell
cd "C:\Users\sethy\MyProjects\Mochi-s-Wealth-Wellness-Hub"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn wealth_wellness_hub.main:app --reload --port 8080
```

Open: http://127.0.0.1:8080

## Alignment to judging criteria
- Innovation: integrated score engine + scenario cockpit + action intelligence.
- Technology and prototype: complete API-backed web app with simulation logic.
- User experience: interactive dashboard with fast feedback loops.
- Feasibility and impact: modular architecture, realistic metrics, adviser-ready actions.
- Market potential: B2B2C model for banks, wealth advisers, and fintech super apps.
