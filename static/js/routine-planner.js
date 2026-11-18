// AeroFamily - Low-Emission Daily Routine Planner Module (Clean White Edition)

const RoutinePlanner = {
  currentPlan: null,

  init() {
    this.setupEventListeners();
    this.generatePlan();
  },

  setupEventListeners() {
    const refreshBtn = document.getElementById("refresh-plan-btn");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => this.generatePlan());
    }

    const printBtn = document.getElementById("print-plan-btn");
    if (printBtn) {
      printBtn.addEventListener("click", () => window.print());
    }
  },

  async generatePlan() {
    const container = document.getElementById("routine-timeline-container");
    if (!container) return;

    container.innerHTML = `
      <div class="py-12 flex flex-col items-center justify-center text-slate-500 space-y-3">
        <div class="w-8 h-8 border-2 border-slate-900 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-sm">Synthesizing low-emission diurnal schedule for ${App.getCurrentCity().name}...</p>
      </div>
    `;

    try {
      const city = App.getCurrentCity();
      const profile = App.getFamilyProfile();

      const response = await fetch("/api/routine/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cityKey: city.id,
          familyProfile: profile,
          targetDate: "Today's Inversion Cycle"
        })
      });

      if (!response.ok) throw new Error("Plan generation failed");

      const data = await response.json();
      this.currentPlan = data;
      this.renderPlan(data);
    } catch (err) {
      console.error(err);
      this.renderFallbackPlan();
    }
  },

  renderPlan(data) {
    const { metrics, schedule, city } = data;
    const container = document.getElementById("routine-timeline-container");
    if (!container) return;

    // Render Impact Metrics Header
    const metricsHtml = `
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="p-4 rounded-2xl border border-emerald-200 bg-emerald-50 shadow-sm">
          <div class="text-xs text-emerald-800 font-bold mb-1 flex items-center space-x-1">
            <span>🫁 Lungs Protected</span>
          </div>
          <div class="text-2xl font-extrabold text-emerald-950 font-mono">-${metrics.exposureReductionPct}%</div>
          <div class="text-[11px] text-emerald-800 mt-1">
            Inhaled PM2.5: <span class="line-through text-red-600 font-semibold">${metrics.baselineInhaledUg}µg</span> → <span class="text-emerald-900 font-bold">${metrics.optimizedInhaledUg}µg</span>
          </div>
        </div>

        <div class="p-4 rounded-2xl border border-amber-200 bg-amber-50 shadow-sm">
          <div class="text-xs text-amber-800 font-bold mb-1 flex items-center space-x-1">
            <span>🚬 Cigarettes Spared</span>
          </div>
          <div class="text-2xl font-extrabold text-amber-950 font-mono">${metrics.cigarettesSaved} <span class="text-xs font-normal text-amber-800">cigs/day</span></div>
          <div class="text-[11px] text-amber-800 mt-1">
            Berkeley Earth equivalency averted per person
          </div>
        </div>

        <div class="p-4 rounded-2xl border border-slate-200 bg-slate-50 shadow-sm">
          <div class="text-xs text-slate-700 font-bold mb-1 flex items-center space-x-1">
            <span>🌱 CO2e Prevented</span>
          </div>
          <div class="text-2xl font-extrabold text-slate-950 font-mono">-${metrics.co2SavedKg} <span class="text-xs font-normal text-slate-600">kg/day</span></div>
          <div class="text-[11px] text-slate-600 mt-1">
            Via trip consolidation & clean heating
          </div>
        </div>

        <div class="p-4 rounded-2xl border border-purple-200 bg-purple-50 shadow-sm">
          <div class="text-xs text-purple-800 font-bold mb-1 flex items-center space-x-1">
            <span>🚗 Tailpipe Soot Cut</span>
          </div>
          <div class="text-2xl font-extrabold text-purple-950 font-mono">-${metrics.tailpipePmSavedG} <span class="text-xs font-normal text-purple-800">g PM</span></div>
          <div class="text-[11px] text-purple-800 mt-1">
            Exhaust particulate eliminated from streets
          </div>
        </div>
      </div>
    `;

    // Render Timeline Items
    const timelineItemsHtml = schedule.map((slot, idx) => {
      const isVentilation = slot.timeSlot.includes("12:30");
      const borderColor = isVentilation ? "border-emerald-300" : "border-slate-200";
      const badgeBg = isVentilation ? "bg-emerald-100 text-emerald-800 border-emerald-200" : "bg-slate-100 text-slate-800 border-slate-300";

      return `
        <div class="relative pl-8 pb-8 border-l-2 border-slate-200 last:border-l-0 last:pb-0">
          <!-- Timeline Node Bullet -->
          <div class="absolute -left-[9px] top-0 w-4 h-4 rounded-full ${isVentilation ? 'bg-emerald-600 ring-4 ring-emerald-100' : 'bg-slate-900 ring-4 ring-slate-100'}"></div>
          
          <div class="bg-white p-5 rounded-2xl border ${borderColor} hover:border-slate-400 transition-all shadow-sm">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
              <div class="flex items-center space-x-2">
                <span class="font-mono text-sm font-bold text-slate-950 px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200">
                  ${slot.timeSlot}
                </span>
                <span class="text-xs font-bold px-2.5 py-1 rounded-full border ${badgeBg}">
                  ${slot.period}
                </span>
              </div>
              <div class="text-xs font-semibold text-amber-800 flex items-center space-x-1">
                <span>⚠️ ${slot.outdoorSmogStatus}</span>
              </div>
            </div>

            <!-- Comparison Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs mb-3">
              <div class="p-3.5 rounded-xl bg-red-50 border border-red-200">
                <div class="text-red-800 font-bold mb-1 flex items-center space-x-1">
                  <span>❌ Unconscious / High-Risk Habit:</span>
                </div>
                <p class="text-red-950 leading-relaxed">${slot.baselineAction}</p>
              </div>

              <div class="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200">
                <div class="text-emerald-800 font-bold mb-1 flex items-center space-x-1">
                  <span>✨ AeroFamily Smog-Defending Shift:</span>
                </div>
                <p class="text-emerald-950 leading-relaxed font-semibold">${slot.recommendedAction}</p>
              </div>
            </div>

            <!-- Direct Impact Banner -->
            <div class="flex flex-wrap items-center justify-between gap-2 pt-2.5 border-t border-slate-100 text-xs">
              <div class="flex items-center space-x-2 text-slate-800">
                <span class="font-bold text-slate-600">Direct Impact:</span>
                <span class="font-semibold text-slate-950">${slot.directImpact}</span>
              </div>
              <div class="px-2.5 py-1 rounded bg-slate-100 text-slate-700 font-mono text-[11px] border border-slate-200 font-medium">
                Emission Saver: ${slot.emissionSaving}
              </div>
            </div>
          </div>
        </div>
      `;
    }).join("");

    container.innerHTML = `
      ${metricsHtml}
      <div class="space-y-2 mt-4">
        ${timelineItemsHtml}
      </div>
    `;
  },

  renderFallbackPlan() {
    const container = document.getElementById("routine-timeline-container");
    if (!container) return;

    container.innerHTML = `
      <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-700">
        <p>Using localized offline routine recommendations. Check that the server is online to generate dynamic machine-calculated plans.</p>
      </div>
    `;
  }
};
