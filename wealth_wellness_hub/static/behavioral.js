const interventionForm = document.getElementById("interventionForm");
const stressForm = document.getElementById("stressForm");
const interventionChecks = document.getElementById("interventionChecks");
const stressOutput = document.getElementById("stressOutput");
const interventionModal = document.getElementById("interventionModal");
const modalContent = document.getElementById("modalContent");

let latestIntervention = null;
let cooldownEndsAt = null;
let cooldownTimer = null;

function money(v) {
  return new Intl.NumberFormat("en-SG", { style: "currency", currency: "SGD", maximumFractionDigits: 0 }).format(v);
}

function setSliderOutputs(form) {
  if (!form) {
    return;
  }
  form.querySelectorAll("input[type=range]").forEach((input) => {
    const output = form.querySelector(`.val[data-for='${input.name}']`);
    const update = () => {
      if (!output) {
        return;
      }
      output.textContent = input.name.includes("pct") ? `${Number(input.value).toFixed(input.step === "0.5" ? 1 : 0)}%` : input.value;
    };
    input.addEventListener("input", update);
    update();
  });
}

function openModal(html) {
  modalContent.innerHTML = html;
  interventionModal.classList.remove("is-hidden");
  interventionModal.setAttribute("aria-hidden", "false");
}

function closeModal() {
  interventionModal.classList.add("is-hidden");
  interventionModal.setAttribute("aria-hidden", "true");
}

function formatCountdown() {
  if (!cooldownEndsAt) {
    return "00:00:00";
  }
  const remaining = Math.max(0, Math.floor((cooldownEndsAt - Date.now()) / 1000));
  const hours = String(Math.floor(remaining / 3600)).padStart(2, "0");
  const minutes = String(Math.floor((remaining % 3600) / 60)).padStart(2, "0");
  const seconds = String(remaining % 60).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

function renderStageTwo() {
  openModal(`
    <p class="modal-tag">Stage 2 · Cooldown</p>
    <h3>Trade placed into protection hold</h3>
    <p>${latestIntervention.stage_two.message}</p>
    <div class="countdown">${formatCountdown()}</div>
    <div class="modal-actions">
      <button type="button" class="ghost-button modal-cancel">Cancel Trade</button>
    </div>
  `);

  const countdownNode = modalContent.querySelector(".countdown");
  const cancelButton = modalContent.querySelector(".modal-cancel");
  cancelButton.addEventListener("click", () => {
    clearInterval(cooldownTimer);
    cooldownEndsAt = null;
    closeModal();
  });

  clearInterval(cooldownTimer);
  cooldownTimer = setInterval(() => {
    if (!countdownNode) {
      clearInterval(cooldownTimer);
      return;
    }
    countdownNode.textContent = formatCountdown();
  }, 1000);
}

function renderStageOne() {
  openModal(`
    <p class="modal-tag">Stage 1 · Intercept</p>
    <h3>Volatility alert</h3>
    <p>${latestIntervention.stage_one.message}</p>
    <div class="modal-actions">
      <button type="button" class="ghost-button modal-cancel">Cancel Trade</button>
      <button type="button" class="modal-proceed">Proceed Anyway</button>
    </div>
  `);

  modalContent.querySelector(".modal-cancel").addEventListener("click", closeModal);
  modalContent.querySelector(".modal-proceed").addEventListener("click", () => {
    cooldownEndsAt = Date.now() + latestIntervention.stage_two.countdown_seconds * 1000;
    renderStageTwo();
    interventionChecks.innerHTML += `
      <div class="watch-item">
        <div class="watch-head">
          <strong>Adviser Action Triggered</strong>
          <span class="watch-status">Queued</span>
        </div>
        <p>${latestIntervention.stage_three.adviser_alert}</p>
      </div>
    `;
  });
}

function renderChecks(data) {
  interventionChecks.innerHTML = `
    <div class="watch-item">
      <div class="watch-head">
        <strong>Logic Check 1</strong>
        <span class="watch-status">${data.triggered ? "Triggered" : "Clear"}</span>
      </div>
      <p>Trade size is ${data.checks.trade_size_pct_liquid_net_worth}% of liquid net worth. Behavioral score is ${data.checks.behavioral_score}/100.</p>
    </div>
  `;
}

if (interventionForm) {
  interventionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(interventionForm).entries());
    payload.trade_amount = Number(String(payload.trade_amount).replace(/,/g, ""));
    payload.unrealized_loss_pct = Number(payload.unrealized_loss_pct);

    const response = await fetch("/api/intervention", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    latestIntervention = await response.json();
    renderChecks(latestIntervention);
    if (latestIntervention.triggered) {
      renderStageOne();
    }
  });
}

if (stressForm) {
  stressForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(stressForm).entries());
    payload.rate_hike_pct = Number(payload.rate_hike_pct);
    payload.market_crash_pct = Number(payload.market_crash_pct);
    payload.income_loss_months = Number(payload.income_loss_months);

    const response = await fetch("/api/stress-test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    stressOutput.innerHTML = `
      <div class="watch-item">
        <div class="watch-head">
          <strong>Stress Test Result</strong>
          <span class="watch-status">Simulated</span>
        </div>
        <p>${data.outputs.message}</p>
        <p>New monthly mortgage payment: ${money(data.outputs.mortgage_payment)}. Monthly burn: ${money(data.outputs.monthly_cash_burn)}. Post-crash equities: ${money(data.outputs.post_crash_equity_value)}.</p>
        <p><strong>Suggestion:</strong> ${data.outputs.recommendation}</p>
      </div>
    `;
  });
}

if (interventionModal) {
  interventionModal.addEventListener("click", (event) => {
    if (event.target === interventionModal) {
      closeModal();
    }
  });
}

setSliderOutputs(interventionForm);
setSliderOutputs(stressForm);
