// AeroFamily - Indoor Air Quality (IAQ) Hacks & DIY Engineering Lab (Clean White Edition)

const IAQLab = {
  init() {
    this.renderHacksList();
    this.setupCADRCalculator();
    this.setupHumiditySimulator();
  },

  renderHacksList() {
    const container = document.getElementById("iaq-hacks-grid");
    if (!container) return;

    container.innerHTML = AERO_DATA.iaqHacks.map(hack => `
      <div class="bg-white p-5 rounded-2xl border border-slate-200 hover:border-slate-400 transition-all flex flex-col justify-between shadow-sm">
        <div>
          <div class="flex items-start justify-between gap-2 mb-2">
            <h3 class="font-bold text-slate-950 text-base">${hack.title}</h3>
            <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-800 border border-slate-300 whitespace-nowrap">
              ${hack.difficulty}
            </span>
          </div>

          <div class="flex flex-wrap gap-2 text-xs mb-3 font-mono">
            <span class="text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 font-semibold">💰 ${hack.cost}</span>
            <span class="text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-semibold">⚡ ${hack.cadRate}</span>
          </div>

          <p class="text-xs text-slate-600 mb-3 leading-relaxed">
            ${hack.effectiveness}
          </p>

          <div class="mb-3">
            <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Materials Needed:</div>
            <ul class="text-xs text-slate-700 space-y-1 list-disc list-inside">
              ${hack.materials.map(m => `<li>${m}</li>`).join("")}
            </ul>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-100">
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700">
            <strong class="text-slate-950">Pro Tip:</strong> ${hack.proTips}
          </div>
        </div>
      </div>
    `).join("");
  },

  setupCADRCalculator() {
    const lengthInput = document.getElementById("cadr-length");
    const widthInput = document.getElementById("cadr-width");
    const heightInput = document.getElementById("cadr-height");
    const achInput = document.getElementById("cadr-ach");
    const achValDisplay = document.getElementById("cadr-ach-val");

    const updateCalc = async () => {
      const length = parseFloat(lengthInput?.value || 18);
      const width = parseFloat(widthInput?.value || 15);
      const height = parseFloat(heightInput?.value || 9);
      const ach = parseFloat(achInput?.value || 5.0);

      if (achValDisplay) achValDisplay.innerText = `${ach} ACH`;

      try {
        const res = await fetch("/api/iaq/cadr-calculator", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            roomLengthFt: length,
            roomWidthFt: width,
            ceilingHeightFt: height,
            desiredACH: ach
          })
        });

        if (!res.ok) throw new Error("CADR Calculation failed");
        const data = await res.json();
        this.renderCADRResults(data);
      } catch (err) {
        console.error(err);
        this.renderLocalCADRResults(length, width, height, ach);
      }
    };

    [lengthInput, widthInput, heightInput, achInput].forEach(elem => {
      if (elem) elem.addEventListener("input", updateCalc);
    });

    // Run initial calc
    updateCalc();
  },

  renderCADRResults(data) {
    const resBox = document.getElementById("cadr-results-box");
    if (!resBox) return;

    const { roomAreaSqFt, roomVolumeCuFt, requiredCadrCFM, crBoxRecommendation } = data;

    resBox.innerHTML = `
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <div class="p-3.5 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <div class="text-[11px] text-slate-500 font-semibold">Room Volume</div>
          <div class="text-lg font-extrabold text-slate-950 font-mono">${Math.round(roomVolumeCuFt)} <span class="text-xs font-normal">cu.ft</span></div>
          <div class="text-[10px] text-slate-500">${roomAreaSqFt} sq.ft</div>
        </div>

        <div class="p-3.5 rounded-2xl bg-slate-900 border border-slate-900 shadow-sm text-white">
          <div class="text-[11px] text-slate-300 font-semibold">Target Clean Air</div>
          <div class="text-lg font-extrabold text-white font-mono">${requiredCadrCFM} <span class="text-xs font-normal">CFM</span></div>
          <div class="text-[10px] text-slate-300">Required Air Delivery</div>
        </div>

        <div class="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 shadow-sm">
          <div class="text-[11px] text-emerald-800 font-bold">C-R Box Units</div>
          <div class="text-lg font-extrabold text-emerald-950 font-mono">${crBoxRecommendation.unitsNeeded} <span class="text-xs font-normal">Unit(s)</span></div>
          <div class="text-[10px] text-emerald-700 font-medium">${crBoxRecommendation.recommendedSpeed}</div>
        </div>

        <div class="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 shadow-sm">
          <div class="text-[11px] text-amber-800 font-bold">Money Saved</div>
          <div class="text-lg font-extrabold text-amber-950 font-mono">+₹${Math.round(crBoxRecommendation.savingsINR || (crBoxRecommendation.savingsUSD * 83)).toLocaleString('en-IN')}</div>
          <div class="text-[10px] text-amber-700">vs commercial HEPA</div>
        </div>
      </div>

      <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-2">
        <div class="flex items-center justify-between text-slate-700">
          <span>Effective Air Changes / Hour:</span>
          <span class="font-extrabold text-emerald-800 font-mono">${crBoxRecommendation.effectiveACH} ACH (Clean Air Room)</span>
        </div>
        <div class="flex items-center justify-between text-slate-700">
          <span>Noise Level:</span>
          <span class="font-mono text-slate-800">${crBoxRecommendation.noiseLevel}</span>
        </div>
        <div class="flex items-center justify-between text-slate-700">
          <span>Filter Replacement Frequency:</span>
          <span class="font-mono text-slate-950 font-bold">Every ${crBoxRecommendation.filterReplacementCycleDays} days during winter peak</span>
        </div>
      </div>
    `;
  },

  renderLocalCADRResults(l, w, h, ach) {
    const vol = l * w * h;
    const reqCfm = Math.round((vol * ach) / 60);
    const units = Math.max(1, Math.ceil(reqCfm / 340));
    this.renderCADRResults({
      roomAreaSqFt: l * w,
      roomVolumeCuFt: vol,
      requiredCadrCFM: reqCfm,
      crBoxRecommendation: {
        unitsNeeded: units,
        recommendedSpeed: "Speed 2 (Quiet Medium)",
        effectiveACH: Math.round((units * 340 * 60) / vol * 10) / 10,
        savingsUSD: (380 - 75) * units,
        savingsINR: (31500 - 6000) * units,
        filterReplacementCycleDays: 90,
        noiseLevel: "38 - 44 dB"
      }
    });
  },

  setupHumiditySimulator() {
    const waterTypeSelect = document.getElementById("water-type-select");
    const humidResult = document.getElementById("humidifier-sim-result");

    const updateSim = () => {
      const type = waterTypeSelect?.value || "tap";
      if (!humidResult) return;

      if (type === "tap") {
        humidResult.innerHTML = `
          <div class="p-4 rounded-2xl bg-red-50 border border-red-200 text-xs space-y-2">
            <div class="flex items-center space-x-2 text-red-800 font-bold text-sm">
              <span>⚠️ HAZARD DETECTED: Tap Water in Ultrasonic Humidifier</span>
            </div>
            <p class="text-red-950 leading-relaxed">
              Tap water contains dissolved minerals (calcium, magnesium, chlorine, salts). The ultrasonic high-frequency diaphragm violently shatters water droplets, creating an aerosol of microscopic solid mineral particles: <strong>Synthetic PM2.5 White Dust</strong>.
            </p>
            <div class="p-2.5 rounded bg-white border border-red-200 font-mono text-red-700 text-[11px] font-bold">
              Expected Indoor PM2.5 Spike: +180 to +350 µg/m³ of mineral irritants inside your bedroom!
            </div>
            <div class="text-emerald-800 font-bold">
              ✓ Solution: Immediately switch to distilled water, reverse osmosis (RO) water, or use an Evaporative Wick Humidifier.
            </div>
          </div>
        `;
      } else if (type === "distilled") {
        humidResult.innerHTML = `
          <div class="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs space-y-2">
            <div class="flex items-center space-x-2 text-emerald-800 font-bold text-sm">
              <span>✨ SAFE PROTOCOL: Distilled / RO Water Active</span>
            </div>
            <p class="text-emerald-950 leading-relaxed">
              Zero dissolved minerals. Only pure H2O vapor is emitted. Airway mucosal membranes remain hydrated without inducing particulate inflammation.
            </p>
            <div class="p-2.5 rounded bg-white border border-emerald-200 font-mono text-emerald-800 text-[11px] font-bold">
              Indoor Mineral PM2.5: 0 µg/m³ (Optimal 45% Relative Humidity achieved)
            </div>
          </div>
        `;
      } else {
        humidResult.innerHTML = `
          <div class="p-4 rounded-2xl bg-slate-50 border border-slate-300 text-xs space-y-2">
            <div class="flex items-center space-x-2 text-slate-950 font-bold text-sm">
              <span>🌱 GOLD STANDARD: Evaporative Wick Humidifier</span>
            </div>
            <p class="text-slate-700 leading-relaxed">
              Evaporative humidifiers draw dry air through a moist paper wick. Only pure water molecules evaporate into the air; all minerals, salts, and hard deposits stay trapped in the paper cartridge. Safe to use with normal tap water!
            </p>
            <div class="p-2.5 rounded bg-white border border-slate-200 font-mono text-slate-900 text-[11px] font-bold">
              Mineral PM2.5 Emission: 0 µg/m³ | Self-regulating humidity cutoff
            </div>
          </div>
        `;
      }
    };

    if (waterTypeSelect) {
      waterTypeSelect.addEventListener("change", updateSim);
      updateSim();
    }
  }
};
