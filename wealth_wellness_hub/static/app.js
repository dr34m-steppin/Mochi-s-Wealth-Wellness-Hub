const metricCards = document.getElementById("metricCards");
const allocationBars = document.getElementById("allocationBars");
const recommendations = document.getElementById("recommendations");
const trendSvg = document.getElementById("trend");
const form = document.getElementById("scenarioForm");
const scenarioNote = document.getElementById("scenarioNote");

function money(v) {
  return new Intl.NumberFormat("en-SG", { style: "currency", currency: "SGD", maximumFractionDigits: 0 }).format(v);
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

  metricCards.innerHTML = items.map(([label, value, delta]) => `
    <article class="metric">
      <div class="label">${label}</div>
      <div class="value">${value}</div>
      <div class="delta">${delta}</div>
    </article>
  `).join("");
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
  renderMetrics(data.overview);
  renderAllocation(data.allocation);
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
