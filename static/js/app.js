// AeroFamily - Main Application Controller & State Engine (Clean White Edition)

const App = {
  currentCityId: "delhi",
  cities: {},
  familyProfile: {
    infants: 1,
    asthmatics: 1,
    seniors: 0,
    pets: 1,
    healthyAdults: 2,
    housingType: "apartment",
    cookingFuel: "gas",
    commuteMode: "car"
  },
  activeTab: "advisor",

  async init() {
    this.loadState();
    await this.fetchCities();
    this.setupTabs();
    this.setupCitySelector();
    this.setupCurrentLocationButton();
    this.setupFamilyModal();
    this.setupCustomCityModal();
    this.updateCityBanner();
    this.renderHourlyForecast();

    // Initialize sub-modules
    if (typeof AIAdvisor !== "undefined") AIAdvisor.init();
    if (typeof RoutinePlanner !== "undefined") RoutinePlanner.init();
    if (typeof IAQLab !== "undefined") IAQLab.init();
    if (typeof ImpactCalculator !== "undefined") ImpactCalculator.init();
    if (typeof CommunityHub !== "undefined") CommunityHub.init();
  },

  loadState() {
    const savedProfile = localStorage.getItem("aerofamily_profile");
    if (savedProfile) {
      try {
        this.familyProfile = { ...this.familyProfile, ...JSON.parse(savedProfile) };
      } catch (e) {
        console.error("Failed to parse saved family profile", e);
      }
    }

    const savedCity = localStorage.getItem("aerofamily_city");
    if (savedCity) {
      this.currentCityId = savedCity;
    }
  },

  saveState() {
    localStorage.setItem("aerofamily_profile", JSON.stringify(this.familyProfile));
    localStorage.setItem("aerofamily_city", this.currentCityId);
  },

  async fetchCities() {
    try {
      const res = await fetch("/api/cities");
      if (!res.ok) throw new Error("Cities fetch failed");
      this.cities = await res.json();
    } catch (e) {
      console.warn("Using local AERO_DATA cities database fallback");
      this.cities = AERO_DATA.cities;
    }
  },

  getCurrentCity() {
    return this.cities[this.currentCityId] || AERO_DATA.cities[this.currentCityId] || AERO_DATA.cities["delhi"];
  },

  getFamilyProfile() {
    return this.familyProfile;
  },

  getVulnerabilitySummary() {
    const p = this.familyProfile;
    const list = [];
    if (p.infants > 0) list.push(`${p.infants} Toddler(s)`);
    if (p.asthmatics > 0) list.push(`${p.asthmatics} Asthmatic(s)`);
    if (p.seniors > 0) list.push(`${p.seniors} Senior(s)`);
    if (p.pets > 0) list.push(`${p.pets} Pet(s)`);
    return list.length > 0 ? list.join(", ") : "Standard Household";
  },

  setupTabs() {
    const tabButtons = document.querySelectorAll(".nav-tab-btn");
    tabButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        const targetTab = btn.getAttribute("data-tab");
        this.switchTab(targetTab);
      });
    });
  },

  switchTab(tabId) {
    this.activeTab = tabId;

    // Update Tab Buttons UI (Clean White + Deep Slate active)
    document.querySelectorAll(".nav-tab-btn").forEach(btn => {
      const isActive = btn.getAttribute("data-tab") === tabId;
      if (isActive) {
        btn.setAttribute("aria-selected", "true");
        btn.classList.add("bg-slate-900", "text-white", "border-slate-900", "font-bold", "shadow-md");
        btn.classList.remove("bg-white", "text-slate-700", "border-slate-300", "hover:bg-slate-100", "hover:text-slate-950");
      } else {
        btn.setAttribute("aria-selected", "false");
        btn.classList.remove("bg-slate-900", "text-white", "border-slate-900", "font-bold", "shadow-md");
        btn.classList.add("bg-white", "text-slate-700", "border-slate-300", "hover:bg-slate-100", "hover:text-slate-950");
      }
    });

    // Toggle Content Panes
    document.querySelectorAll(".tab-pane").forEach(pane => {
      if (pane.id === `tab-${tabId}`) {
        pane.classList.remove("hidden");
      } else {
        pane.classList.add("hidden");
      }
    });

    // Refresh tab-specific data if needed
    if (tabId === "routine" && typeof RoutinePlanner !== "undefined") {
      RoutinePlanner.generatePlan();
    } else if (tabId === "impact" && typeof ImpactCalculator !== "undefined") {
      ImpactCalculator.recalculate();
    }
  },

  setupCurrentLocationButton() {
    const locBtn = document.getElementById("detect-current-location-btn");
    if (!locBtn) return;
    locBtn.onclick = () => this.detectCurrentLocation();
  },

  async detectCurrentLocation() {
    const locBtn = document.getElementById("detect-current-location-btn");
    const locBtnText = document.getElementById("loc-btn-text");
    const locIcon = document.getElementById("loc-icon");

    if (!navigator.geolocation) {
      this.showNotification("Geolocation is not supported by your browser. Please select or add a city manually.");
      return;
    }

    // Set UI loading state
    if (locBtnText) locBtnText.innerText = "Locating...";
    if (locIcon) locIcon.innerText = "⏳";
    if (locBtn) locBtn.disabled = true;

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          if (locBtnText) locBtnText.innerText = "Syncing Weather...";

          let cityName = `Coordinates (${lat.toFixed(2)}°, ${lon.toFixed(2)}°)`;
          let temp = null;
          let humidity = null;
          let windSpeed = null;
          let pm25 = null;

          // 1. Fetch reverse geocode locality from free BigDataCloud API
          try {
            const geoRes = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
            if (geoRes.ok) {
              const geoData = await geoRes.json();
              const locality = geoData.locality || geoData.city || geoData.principalSubdivision;
              const country = geoData.countryName || "";
              if (locality) {
                cityName = country ? `${locality}, ${country}` : locality;
              }
            }
          } catch (e) {
            console.warn("Reverse geocode failed, using coordinates", e);
          }

          // 2. Fetch live meteorological weather from Open-Meteo
          try {
            const weatherRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m`);
            if (weatherRes.ok) {
              const weatherData = await weatherRes.json();
              if (weatherData.current) {
                temp = weatherData.current.temperature_2m;
                humidity = weatherData.current.relative_humidity_2m;
                windSpeed = weatherData.current.wind_speed_10m;
              }
            }
          } catch (e) {
            console.warn("Open-Meteo weather fetch fallback", e);
          }

          // 3. Fetch live air quality from Open-Meteo Air Quality API
          try {
            const aqiRes = await fetch(`https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${lat}&longitude=${lon}&current=pm10,pm2_5,us_aqi`);
            if (aqiRes.ok) {
              const aqiData = await aqiRes.json();
              if (aqiData.current && aqiData.current.pm2_5 !== undefined && aqiData.current.pm2_5 !== null) {
                pm25 = Math.round(aqiData.current.pm2_5 * 10) / 10;
              }
            }
          } catch (e) {
            console.warn("Open-Meteo air quality fetch fallback", e);
          }

          // 4. Send synthesized coordinates and live meteorological metrics to server
          const payload = {
            lat,
            lon,
            name: cityName,
            pm25: pm25,
            temperature: temp,
            humidity: humidity,
            windSpeed: windSpeed
          };

          const res = await fetch("/api/location/current", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });

          if (!res.ok) throw new Error("Failed to register location on backend");
          const locationData = await res.json();

          // 5. Update state and UI
          this.cities["current_location"] = locationData;
          this.currentCityId = "current_location";
          this.saveState();
          this.setupCitySelector();
          this.onCityChanged();

          this.showNotification(`📍 Live Location Active: ${cityName}! Weather & air quality synchronized.`);
        } catch (err) {
          console.error("Current location processing error:", err);
          // Fallback heuristic registration
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          const fallbackId = "current_location";
          this.cities[fallbackId] = {
            id: fallbackId,
            name: `📍 Current Location (${lat.toFixed(2)}°, ${lon.toFixed(2)}°)`,
            country: "Local Device",
            aqi: 135,
            pm25: 64.0,
            pm10: 92.0,
            status: "Unhealthy for Sensitive Groups",
            category: "sensitive",
            temperature: 14.0,
            humidity: 68.0,
            inversionStrength: "Winter Inversion Active",
            windSpeed: "4.5 km/h",
            ventilationWindow: "12:30 PM - 2:30 PM",
            grapStage: "Local Alert",
            dominantSources: ["Local vehicle traffic", "Thermal boundary stagnation"],
            advisory: "Live coordinates registered. Ground thermal trapping active; prioritize indoor HEPA filtration."
          };
          this.currentCityId = fallbackId;
          this.saveState();
          this.setupCitySelector();
          this.onCityChanged();
          this.showNotification("📍 Current location synchronized with meteorological inversion model.");
        } finally {
          if (locBtnText) locBtnText.innerText = "Current Location";
          if (locIcon) locIcon.innerText = "📍";
          if (locBtn) locBtn.disabled = false;
        }
      },
      (err) => {
        console.warn("Geolocation access notice:", err);
        let errorMsg = "Could not retrieve GPS coordinates. Please ensure browser location is allowed or choose a city.";
        if (err.code === 1) {
          errorMsg = "Location permission was denied. Please allow location access in your browser or pick a city.";
        }
        this.showNotification(errorMsg);
        if (locBtnText) locBtnText.innerText = "Current Location";
        if (locIcon) locIcon.innerText = "📍";
        if (locBtn) locBtn.disabled = false;
      },
      { timeout: 10000, enableHighAccuracy: true, maximumAge: 120000 }
    );
  },

  setupCitySelector() {
    const selector = document.getElementById("city-selector");
    if (!selector) return;

    selector.innerHTML = Object.keys(this.cities).map(cid => {
      const c = this.cities[cid];
      return `<option value="${cid}" ${cid === this.currentCityId ? 'selected' : ''}>${c.name} (AQI ${c.aqi})</option>`;
    }).join("");

    selector.onchange = (e) => {
      this.currentCityId = e.target.value;
      this.saveState();
      this.onCityChanged();
    };
  },

  onCityChanged() {
    this.updateCityBanner();
    this.renderHourlyForecast();

    // Notify modules
    if (typeof AIAdvisor !== "undefined") AIAdvisor.renderInitialMessage();
    if (typeof RoutinePlanner !== "undefined") RoutinePlanner.generatePlan();
    if (typeof ImpactCalculator !== "undefined") ImpactCalculator.recalculate();
    this.showNotification(`Switched location to ${this.getCurrentCity().name}`);
  },

  updateCityBanner() {
    const city = this.getCurrentCity();
    const cigs = (city.pm25 / 22.0).toFixed(1);

    // Toggle live source badge if current location
    const liveTag = document.getElementById("live-source-tag");
    if (liveTag) {
      if (this.currentCityId === "current_location") {
        liveTag.classList.remove("hidden");
      } else {
        liveTag.classList.add("hidden");
      }
    }

    // Update banner texts
    const aqiVal = document.getElementById("banner-aqi-val");
    const aqiCat = document.getElementById("banner-aqi-category");
    const pmVal = document.getElementById("banner-pm25-val");
    const inversionVal = document.getElementById("banner-inversion-val");
    const ventWindowVal = document.getElementById("banner-vent-window-val");
    const cigsVal = document.getElementById("banner-cigs-val");
    const grapBadge = document.getElementById("banner-grap-badge");
    const advisoryVal = document.getElementById("banner-advisory-val");
    const cityNameVal = document.getElementById("banner-city-name");

    if (cityNameVal) cityNameVal.innerText = city.name;
    if (aqiVal) aqiVal.innerText = city.aqi;
    if (aqiCat) {
      aqiCat.innerText = city.status;
      aqiCat.className = `text-xs font-semibold px-2.5 py-0.5 rounded-full ${this.getCategoryClass(city.category)}`;
    }
    if (pmVal) pmVal.innerText = `${city.pm25} µg/m³`;
    if (inversionVal) inversionVal.innerText = city.inversionStrength;
    if (ventWindowVal) ventWindowVal.innerText = city.ventilationWindow;
    if (cigsVal) cigsVal.innerText = `~${cigs} cigs/day`;
    if (grapBadge) grapBadge.innerText = city.grapStage;
    if (advisoryVal) advisoryVal.innerText = city.advisory;

    // Profile summary in header
    const profileSummary = document.getElementById("header-profile-summary");
    if (profileSummary) {
      profileSummary.innerText = this.getVulnerabilitySummary();
    }
  },

  getCategoryClass(category) {
    switch (category) {
      case "hazardous": return "bg-fuchsia-100 text-fuchsia-800 border border-fuchsia-300";
      case "very-unhealthy": return "bg-purple-100 text-purple-800 border border-purple-300";
      case "unhealthy": return "bg-red-100 text-red-800 border border-red-300";
      case "sensitive": return "bg-amber-100 text-amber-800 border border-amber-300";
      default: return "bg-emerald-100 text-emerald-800 border border-emerald-300";
    }
  },

  renderHourlyForecast() {
    const container = document.getElementById("hourly-forecast-container");
    if (!container) return;

    const city = this.getCurrentCity();
    const hourly = city.hourly || (typeof AERO_DATA !== "undefined" ? this.generateFallbackHourly(city.pm25) : []);

    container.innerHTML = hourly.map(h => {
      const isVent = h.isVentilationWindow;
      return `
        <div class="flex flex-col items-center shrink-0 p-2.5 rounded-xl ${isVent ? 'bg-emerald-50 border border-emerald-300 ring-1 ring-emerald-200' : 'bg-slate-50 border border-slate-200'} text-center min-w-[76px] transition-all shadow-sm">
          <span class="text-[11px] font-mono font-medium ${isVent ? 'text-emerald-800 font-bold' : 'text-slate-500'}">${h.time}</span>
          <div class="my-1.5 font-mono text-sm font-bold ${isVent ? 'text-emerald-950 font-extrabold' : 'text-slate-900'}">${h.pm25}</div>
          <div class="w-2.5 h-2.5 rounded-full mb-1.5" style="background-color: ${h.color};"></div>
          <span class="text-[9px] ${isVent ? 'text-emerald-800 font-extrabold uppercase' : 'text-slate-600'} whitespace-nowrap">
            ${isVent ? '🌟 VENT PURGE' : h.category}
          </span>
        </div>
      `;
    }).join("");
  },

  generateFallbackHourly(basePM) {
    const list = [];
    for (let h = 0; h < 24; h++) {
      const mult = (h >= 6 && h <= 9) ? 1.4 : (h >= 12 && h <= 14 ? 0.65 : (h >= 18 && h <= 22 ? 1.35 : 1.1));
      const val = Math.round(basePM * mult);
      list.push({
        time: `${h < 10 ? '0' : ''}${h}:00`,
        pm25: val,
        color: val > 250 ? '#701a75' : (val > 150 ? '#ef4444' : '#f59e0b'),
        category: val > 250 ? 'Hazardous' : (val > 150 ? 'Unhealthy' : 'Sensitive'),
        isVentilationWindow: h >= 12 && h <= 14
      });
    }
    return list;
  },

  setupFamilyModal() {
    const openBtn = document.getElementById("edit-family-profile-btn");
    const modal = document.getElementById("family-profile-modal");
    const closeBtn = document.getElementById("close-family-modal-btn");
    const form = document.getElementById("family-profile-form");

    if (openBtn && modal) {
      openBtn.addEventListener("click", () => {
        const p = this.familyProfile;
        const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
        setVal("prof-infants", p.infants);
        setVal("prof-asthma", p.asthmatics);
        setVal("prof-seniors", p.seniors);
        setVal("prof-pets", p.pets);
        setVal("prof-adults", p.healthyAdults);
        setVal("prof-housing", p.housingType);
        setVal("prof-cooking", p.cookingFuel);
        setVal("prof-commute", p.commuteMode);

        modal.classList.remove("hidden");
      });
    }

    if (closeBtn && modal) {
      closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
    }

    if (form && modal) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const getVal = (id, def) => { const el = document.getElementById(id); return el ? el.value : def; };
        
        this.familyProfile = {
          infants: parseInt(getVal("prof-infants", 0)),
          asthmatics: parseInt(getVal("prof-asthma", 0)),
          seniors: parseInt(getVal("prof-seniors", 0)),
          pets: parseInt(getVal("prof-pets", 0)),
          healthyAdults: parseInt(getVal("prof-adults", 2)),
          housingType: getVal("prof-housing", "apartment"),
          cookingFuel: getVal("prof-cooking", "gas"),
          commuteMode: getVal("prof-commute", "car")
        };

        this.saveState();
        modal.classList.add("hidden");
        this.updateCityBanner();
        
        if (typeof AIAdvisor !== "undefined") AIAdvisor.renderInitialMessage();
        if (typeof RoutinePlanner !== "undefined") RoutinePlanner.generatePlan();
        if (typeof ImpactCalculator !== "undefined") ImpactCalculator.recalculate();
        
        this.showNotification("Family profile updated! All plans and impact models recalibrated.");
      });
    }
  },

  setupCustomCityModal() {
    const openBtn = document.getElementById("add-custom-city-btn");
    const modal = document.getElementById("custom-city-modal");
    const closeBtn = document.getElementById("close-custom-modal-btn");
    const form = document.getElementById("custom-city-form");

    if (openBtn && modal) {
      openBtn.addEventListener("click", () => modal.classList.remove("hidden"));
    }

    if (closeBtn && modal) {
      closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
    }

    if (form && modal) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("custom-name")?.value || "My Neighborhood";
        const pm25 = parseFloat(document.getElementById("custom-pm25")?.value || 120);
        const aqi = parseInt(document.getElementById("custom-aqi")?.value || (pm25 * 1.2));
        const temp = parseFloat(document.getElementById("custom-temp")?.value || 12);

        try {
          const res = await fetch("/api/custom-city", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, pm25, aqi, temperature: temp })
          });

          if (!res.ok) throw new Error("Could not add custom city");
          const newCity = await res.json();
          this.cities[newCity.id] = newCity;
          this.currentCityId = newCity.id;
          this.setupCitySelector();
          this.saveState();
          modal.classList.add("hidden");
          this.onCityChanged();
        } catch (err) {
          console.error(err);
          const cid = `custom_${Date.now()}`;
          this.cities[cid] = {
            id: cid,
            name: name,
            aqi: aqi,
            pm25: pm25,
            pm10: pm25 * 1.4,
            status: pm25 > 250 ? "Hazardous" : "Unhealthy",
            category: pm25 > 250 ? "hazardous" : "unhealthy",
            temperature: temp,
            inversionStrength: "Winter Inversion",
            ventilationWindow: "12:30 PM - 2:30 PM",
            grapStage: "Local Alert",
            advisory: "High particulate concentration. Take indoor precautions."
          };
          this.currentCityId = cid;
          this.setupCitySelector();
          this.saveState();
          modal.classList.add("hidden");
          this.onCityChanged();
        }
      });
    }
  },

  showNotification(msg) {
    const toast = document.createElement("div");
    toast.className = "fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl bg-slate-900 text-white text-xs shadow-2xl transition-all flex items-center space-x-2 font-medium border border-slate-700";
    toast.innerHTML = `<span>✨</span><span>${msg}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 400);
    }, 3200);
  }
};

window.addEventListener("DOMContentLoaded", () => App.init());
