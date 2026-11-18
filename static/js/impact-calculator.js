// AeroFamily - Interactive Impact Calculator & Scenario Simulator (Clean White Edition)

const ImpactCalculator = {
  init() {
    this.setupListeners();
    this.recalculate();
  },

  setupListeners() {
    const controls = [
      "sim-mask", "sim-purifier-hours", "sim-sealing",
      "sim-cooking", "sim-commute", "sim-household-size"
    ];

    controls.forEach(id => {
      const elem = document.getElementById(id);
      if (elem) {
        elem.addEventListener("input", () => this.recalculate());
        elem.addEventListener("change", () => this.recalculate());
      }
    });

    const hoursSlider = document.getElementById("sim-purifier-hours");
    const hoursDisplay = document.getElementById("sim-purifier-hours-val");
    if (hoursSlider && hoursDisplay) {
      hoursSlider.addEventListener("input", (e) => {
        hoursDisplay.innerText = `${e.target.value} hrs/day`;
      });
    }
  },

  async recalculate() {
    const city = App.getCurrentCity();
    const mask = document.getElementById("sim-mask")?.value || "n95";
    const hours = parseFloat(document.getElementById("sim-purifier-hours")?.value || 16);
    const sealing = document.getElementById("sim-sealing")?.value || "sealed";
    const cooking = document.getElementById("sim-cooking")?.value || "induction_vented";
    const commute = document.getElementById("sim-commute")?.value || "metro";
    const household = parseInt(document.getElementById("sim-household-size")?.value || 3);

    try {
      const res = await fetch("/api/impact/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cityKey: city.id,
          commuteChoice: commute,
          maskChoice: mask,
          airPurifierHours: hours,
          homeSealing: sealing,
          cookingMode: cooking,
          householdSize: household
        })
      });

      if (!res.ok) throw new Error("Simulation failed");
      const data = await res.json();
      this.renderResults(data, household);
    } catch (err) {
      console.error(err);
      this.renderLocalSimulation(city, mask, hours, sealing, cooking, commute, household);
    }
  },

  renderResults(data, household) {
    const resultContainer = document.getElementById("impact-sim-results");
    if (!resultContainer) return;

    const {
      outdoorPM25,
      indoorCalculatedPM25,
      dailyInhaledUg,
      worstCaseDailyUg,
      ugAvoidedPerDay,
      exposureReductionPct,
      cigarettesAvoidedDaily,
      monthlyCigarettesAvoided,
      co2SavedKgPerDay,
      monthlyCo2SavedKg
    } = data;

    const totalFamilyCigsSaved = Math.round(monthlyCigarettesAvoided * household);

    resultContainer.innerHTML = `
      <!-- Primary Gauge Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <!-- Card 1: Exposure Reduction -->
        <div class="p-5 rounded-2xl border border-emerald-200 bg-emerald-50 text-center shadow-sm">
          <div class="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-1">Total Exposure Reduction</div>
          <div class="text-4xl font-extrabold text-emerald-950 font-mono my-2">-${exposureReductionPct}%</div>
          <div class="text-xs text-emerald-900 font-medium">
            Inhaling <span class="font-bold text-slate-950 font-mono">${dailyInhaledUg} µg/day</span> vs unshielded <span class="line-through text-red-600 font-mono">${worstCaseDailyUg} µg</span>
          </div>
        </div>

        <!-- Card 2: Cigarettes Equivalent -->
        <div class="p-5 rounded-2xl border border-amber-200 bg-amber-50 text-center shadow-sm">
          <div class="text-xs font-bold text-amber-800 uppercase tracking-wider mb-1">Cigarette Particulate Spared</div>
          <div class="text-4xl font-extrabold text-amber-950 font-mono my-2">${cigarettesAvoidedDaily} <span class="text-sm font-normal text-amber-800">cigs/day</span></div>
          <div class="text-xs text-amber-900 font-medium">
            <strong>${monthlyCigarettesAvoided}</strong> cigs spared/month per person (<span class="text-amber-950 font-bold">${totalFamilyCigsSaved}</span> for household)
          </div>
        </div>

        <!-- Card 3: Carbon Avoidance -->
        <div class="p-5 rounded-2xl border border-slate-200 bg-slate-50 text-center shadow-sm">
          <div class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Community CO2e Averted</div>
          <div class="text-4xl font-extrabold text-slate-950 font-mono my-2">-${co2SavedKgPerDay} <span class="text-sm font-normal text-slate-600">kg/day</span></div>
          <div class="text-xs text-slate-700 font-medium">
            <strong class="text-slate-950">${monthlyCo2SavedKg} kg CO2e</strong> saved every 30 days
          </div>
        </div>
      </div>

      <!-- Air Differential Bar -->
      <div class="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm mb-6">
        <div class="flex items-center justify-between text-xs mb-2">
          <span class="text-slate-700 font-semibold">Air Pollution Differential: Outdoor vs Indoor Safe Zone</span>
          <span class="text-emerald-800 font-mono font-bold">${Math.round((1 - indoorCalculatedPM25/outdoorPM25)*100)}% Cleaner Indoors</span>
        </div>
        
        <div class="space-y-3">
          <div>
            <div class="flex justify-between text-xs mb-1 font-mono">
              <span class="text-red-700 font-semibold">Outdoor Ambient Air</span>
              <span class="text-red-700 font-bold">${outdoorPM25} µg/m³ PM2.5</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
              <div class="bg-gradient-to-r from-red-500 to-purple-600 h-3 rounded-full" style="width: 100%"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs mb-1 font-mono">
              <span class="text-emerald-700 font-semibold">Your Shielded Indoor Air</span>
              <span class="text-emerald-700 font-bold">${indoorCalculatedPM25} µg/m³ PM2.5</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
              <div class="bg-gradient-to-r from-emerald-500 to-teal-500 h-3 rounded-full" style="width: ${Math.min(100, Math.max(5, (indoorCalculatedPM25 / outdoorPM25) * 100))}%"></div>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
          <span class="flex items-center space-x-1">
            <span>🛡️ WHO 24h Guideline: 15 µg/m³</span>
          </span>
          <span class="${indoorCalculatedPM25 <= 25 ? 'text-emerald-800 font-bold' : 'text-amber-800 font-bold'}">
            ${indoorCalculatedPM25 <= 15 ? '✓ Compliant with WHO Clean Air Standards' : (indoorCalculatedPM25 <= 25 ? '✓ Good Indoor Protection' : '⚠️ Enhance Sealing / Increase Purifier Runtime')}
          </span>
        </div>
      </div>
    `;
  },

  renderLocalSimulation(city, mask, hours, sealing, cooking, commute, household) {
    const outPM = city.pm25;
    const infil = sealing === "sealed" ? 0.25 : (sealing === "average" ? 0.50 : 0.75);
    const cookPM = cooking === "induction_vented" ? 3 : (cooking === "gas_vented" ? 15 : 45);
    const purEff = (hours / 24) * 0.88;
    const indoorPM = Math.max(6, Math.round((outPM * infil + cookPM) * (1 - purEff) * 10) / 10);
    const worstCase = Math.round((outPM * 0.75 + 45) * 15);
    const dailyInhaled = Math.round(indoorPM * 16 + outPM * 0.1 * 2);
    const avoided = Math.max(0, worstCase - dailyInhaled);
    const pct = Math.round((avoided / worstCase) * 100);

    this.renderResults({
      outdoorPM25: outPM,
      indoorCalculatedPM25: indoorPM,
      dailyInhaledUg: dailyInhaled,
      worstCaseDailyUg: worstCase,
      ugAvoidedPerDay: avoided,
      exposureReductionPct: pct,
      cigarettesAvoidedDaily: Math.round((avoided / 330) * 10) / 10,
      monthlyCigarettesAvoided: Math.round((avoided / 330) * 30),
      co2SavedKgPerDay: commute === "metro" ? 5.9 : 4.6,
      monthlyCo2SavedKg: Math.round((commute === "metro" ? 5.9 : 4.6) * 30)
    }, household);
  }
};
