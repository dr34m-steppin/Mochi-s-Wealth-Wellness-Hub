# SWAN (Sleep Well At Night)

SWAN is a behavioral wealth protection platform built for the FinTech Innovators' Hackathon 2026 Wealth Wellness Hub challenge. It consolidates traditional, private, and digital assets into a single wealth view, then applies wellness analytics to measure diversification, liquidity, and behavioral resilience. Beyond monitoring, SWAN protects investors from emotional wealth destruction: it calculates behavioral alpha leakage, surfaces a dynamic client risk score, predicts panic-selling vulnerability, triggers a volatility intervention protocol before harmful trades execute, and gives advisers visibility into emerging emotional risk. The platform also includes stress testing, editable client wealth composition, and scenario simulation so users can understand how market shocks, income loss, and rate changes affect resilience. In short, SWAN solves the problem statement by turning fragmented wealth data into a proactive, explainable system for financial health monitoring, behavioral risk intervention, and adviser-client decision support.

Demo video: `https://youtu.be/XE6OBVNiC4U`

## Core capabilities
- Unified dashboard for cash, public markets, private assets, and digital assets
- Editable client net worth and wealth composition inputs
- Financial wellness metrics for diversification, liquidity, and behavioral resilience
- Behavioral Protection page with dynamic client score and behavioral alpha leakage
- Volatility Intervention Protocol with intercept, cooldown, and adviser alert logic
- Scenario simulator for market crashes, rate hikes, and income-loss stress tests
- Email login/signup with persistent local user storage

## Tech stack
- Backend: FastAPI
- Frontend: HTML, CSS, vanilla JavaScript
- Data store: SQLite
- Runtime: Python 3.11+

## Quick start
1. Open a terminal in the folder where you want the project.
2. Clone the repository:

```powershell
git clone https://github.com/dr34m-steppin/Mochi-s-Wealth-Wellness-Hub.git
cd Mochi-s-Wealth-Wellness-Hub
```

3. Create a virtual environment:

```powershell
python -m venv .venv
```

4. Activate it:

```powershell
.\.venv\Scripts\activate
```

5. Install dependencies:

```powershell
pip install -r requirements.txt
```

6. Start the web app:

```powershell
python -m uvicorn wealth_wellness_hub.main:app --reload --port 8080
```

7. Open the app in a browser:

```text
http://127.0.0.1:8080
```

## Judge walkthrough
1. Create an account on the login/signup screen.
2. Open the main dashboard and review the unified wealth metrics.
3. Click `Edit` on Net Worth or `Edit Holdings` in Wealth Composition to test client-specific inputs.
4. Run the Scenario Cockpit to simulate portfolio stress.
5. Open `Behavioral Protection` from the top navigation.
6. Review the dynamic client score and behavioral alpha leakage card.
7. Use the trade intervention flow and stress simulator to test SWAN's protection logic.
