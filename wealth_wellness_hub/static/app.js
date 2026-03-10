const metricCards = document.getElementById("metricCards");
const allocationBars = document.getElementById("allocationBars");
const recommendations = document.getElementById("recommendations");
const trendSvg = document.getElementById("trend");
const form = document.getElementById("scenarioForm");
const scenarioNote = document.getElementById("scenarioNote");
const compositionEditor = document.getElementById("compositionEditor");
const editCompositionButton = document.getElementById("editCompositionButton");

let latestDashboard = null;

const metricMeta = {
  "Net Worth": {
    definition: "The total value of all connected assets across cash, public markets, private holdings, and digital wallets.",
    derived: "Calculated as the straight sum of every tracked holding in the unified wallet view.",
  },
  "Wellness Score": {
    definition: "A blended signal for overall financial health, balancing structure, flexibility, and investor behavior.",
    derived: "Weighted from diversification (40%), liquidity (35%), and behavioral resilience (25%).",
  },
  "Risk Heat": {
    definition: "A quick volatility proxy showing how exposed the portfolio is to high-movement asset classes.",
    derived: "Computed from the portfolio's weighted asset volatility, then scaled into an easy-to-read 0-100 heat score.",
  },
  Diversification: {
    definition: "How evenly wealth is spread across asset classes instead of being concentrated in a few sleeves.",
    derived: "Based on concentration across asset-class weights using a normalized concentration index.",
  },
  Liquidity: {
    definition: "How easily the investor can meet near-term cash needs without forcing distressed sales.",
    derived: "Combines the share of assets sellable within 7 days and the months of expenses covered by cash reserves.",
  },
  "Behavioral Resilience": {
    definition: "A measure of how stable decision-making remains under market stress and over long-term saving cycles.",
    derived: "Built from contribution consistency, panic-sell penalties, and a bonus for disciplined rebalancing activity.",
  },
};

function money(v) {
  return new Intl.NumberFormat("en-SG", { style: "currency", currency: "SGD", maximumFractionDigits: 0 }).format(v);
}

function renderMetricCard(label, value, delta) {
  const meta = metricMeta[label];
  const tooltip = meta ? `
    <span class="info-wrap">
      <button type="button" class="info-dot" aria-label="Explain ${label}">i</button>
      <span class="tooltip" role="tooltip">
        <strong>${label}</strong>
        ${meta.definition}
        <br><br>
        <strong>How it's derived</strong>
        ${meta.derived}
      </span>
    </span>
  ` : "";

  return `
    <article class="metric">
      <div class="label">
        <span class="label-text">${label}</span>
        ${tooltip}
      </div>
      <div class="value">${value}</div>
      <div class="delta">${delta}</div>
    </article>
  `;
}

function renderMetrics(overview) {
  const items = [
    ["Net Worth", money(overview.total_net_worth), "Unified across all wallets"],
    ["Wellness Score", `${overview.wellness_score}`, "Composite of 3 core dimensions"],
    ["Risk Heat", `${overview.risk_heat}%`, overview.risk_heat > 55 ? "Volatility elevated" : "Risk posture stable"],
    ["Diversification", `${overview.metrics.diversification}%`, "Concentration awareness"],
    ["Liquidity", `${overview.metrics.liquidity}%`, "Emergency runway health"],
    ["Behavioral Resilience", `${overview.metrics.behavioral_resilience}%`, "Discipline under stress"],
  ];

  metricCards.innerHTML = items.map(([label, value, delta]) => renderMetricCard(label, value, delta)).join("");
}

function renderAllocation(allocation) {
  allocationBars.innerHTML = allocation.map((x) => `
    <div class="bar-row">
      <div>${x.class}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${x.weight}%"></div></div>
      <div>${x.weight}%</div>
    </div>
  `).join("");
}

function renderCompositionEditor(holdings) {
  if (!compositionEditor || !holdings) {
    return;
  }
  compositionEditor.innerHTML = `
    <form id="compositionForm" class="composition-form">
      ${holdings.map((holding, index) => `
        <div class="composition-row">
          <div>
            <div class="composition-name">${holding.name}</div>
            <div class="composition-class">${holding.class}</div>
          </div>
          <label>
            <span>Value (SGD)</span>
            <input type="number" name="value-${index}" value="${Math.round(holding.value)}" min="0" step="100" class="text-input composition-input" />
          </label>
        </div>
      `).join("")}
      <div class="composition-actions">
        <button type="submit">Save Holdings</button>
        <button type="button" class="ghost-button" id="cancelCompositionButton">Cancel</button>
      </div>
    </form>
  `;

  const formNode = document.getElementById("compositionForm");
  const cancelButton = document.getElementById("cancelCompositionButton");

  cancelButton.addEventListener("click", () => {
    compositionEditor.classList.add("is-hidden");
  });

  formNode.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      holdings: holdings.map((holding, index) => ({
        ...holding,
        value: Number(formNode.elements[`value-${index}`].value),
      })),
    };

    const response = await fetch("/api/client-profile/holdings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    compositionEditor.classList.add("is-hidden");
    renderAll(data);
  });
}

function renderTrend(timeline) {
  const width = 500;
  const height = 220;
  const pad = 24;
  const min = Math.min(...timeline.map((t) => t.score)) - 4;
  const max = Math.max(...timeline.map((t) => t.score)) + 4;

  const points = timeline.map((t, i) => {
    const x = pad + (i * (width - pad * 2)) / (timeline.length - 1);
    const y = height - pad - ((t.score - min) / (max - min)) * (height - pad * 2);
    return { ...t, x, y };
  });

  const path = points.map((p) => `${p.x},${p.y}`).join(" ");
  const labels = points.map((p) => `<text x="${p.x}" y="206" fill="#9dc7b9" font-size="10" text-anchor="middle">${p.month}</text>`).join("");
  const dots = points.map((p) => `<circle cx="${p.x}" cy="${p.y}" r="3.8" fill="#53e6b8"/>`).join("");

  trendSvg.innerHTML = `
    <polyline fill="none" stroke="#53e6b8" stroke-width="3" points="${path}" />
    ${dots}
    ${labels}
  `;
}

function renderRecs(recs) {
  recommendations.innerHTML = recs.map((r) => `
    <div class="rec">
      <h3>${r.title}</h3>
      <div class="impact">${r.impact}</div>
      <p>${r.action}</p>
    </div>
  `).join("");
}

async function loadDashboard() {
  const resp = await fetch("/api/dashboard");
  const data = await resp.json();
  renderAll(data);
}

function renderAll(data) {
  latestDashboard = data;
  renderMetrics(data.overview);
  renderAllocation(data.allocation);
  renderCompositionEditor(data.holdings);
  renderTrend(data.timeline);
  renderRecs(data.recommendations);
  if (data.scenario?.note) {
    scenarioNote.textContent = data.scenario.note;
  }
}

function bindSliders() {
  form.querySelectorAll("input[type=range]").forEach((input) => {
    const output = form.querySelector(`.val[data-for='${input.name}']`);
    const update = () => {
      if (input.name === "monthly_contribution") {
        output.textContent = Number(input.value).toLocaleString("en-SG");
      } else if (input.name.includes("pct")) {
        output.textContent = `${input.value}%`;
      } else {
        output.textContent = input.value;
      }
    };
    input.addEventListener("input", update);
    update();
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  payload.equity_shock_pct = Number(payload.equity_shock_pct);
  payload.crypto_shock_pct = Number(payload.crypto_shock_pct);
  payload.monthly_contribution = Number(payload.monthly_contribution);
  payload.emergency_buffer_target_months = Number(payload.emergency_buffer_target_months);

  const resp = await fetch("/api/scenario", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await resp.json();
  renderAll(data);
});

bindSliders();
loadDashboard();

if (editCompositionButton) {
  editCompositionButton.addEventListener("click", () => {
    if (!latestDashboard?.holdings) {
      return;
    }
    compositionEditor.classList.toggle("is-hidden");
    if (!compositionEditor.classList.contains("is-hidden")) {
      renderCompositionEditor(latestDashboard.holdings);
    }
  });
}
