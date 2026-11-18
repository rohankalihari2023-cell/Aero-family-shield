/**
 * @file community-hub.js
 * @description Community Clean Air Action Hub Module.
 * Facilitates citizen reporting of open burning/diesel violations,
 * displays local clean air pods, safe havens, and neighborhood pledges.
 */
"use strict";

const CommunityHub = {
  reports: [],

  init() {
    this.renderCommunityActions();
    this.fetchReports();
    this.setupReportForm();
    this.setupPledges();
  },

  renderCommunityActions() {
    const container = document.getElementById("community-initiatives-list");
    if (!container) return;

    container.innerHTML = AERO_DATA.communityActions.map(action => `
      <div class="bg-white p-5 rounded-2xl border border-slate-200 hover:border-slate-400 transition-all shadow-sm">
        <div class="flex items-start justify-between gap-2 mb-2">
          <h3 class="font-bold text-slate-950 text-base">${action.name}</h3>
          <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-800 border border-slate-300 whitespace-nowrap">
            ${action.category}
          </span>
        </div>

        <p class="text-xs text-slate-600 mb-3 leading-relaxed">
          ${action.description}
        </p>

        <div class="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs mb-3 text-emerald-900 font-medium">
          <strong class="text-emerald-950">Community Impact:</strong> ${action.impact}
        </div>

        <div class="flex items-center justify-between text-xs pt-2 border-t border-slate-100">
          <span class="text-slate-500 font-medium flex items-center space-x-1">
            <span>👥</span>
            <span>${action.participants} Active Neighbors</span>
          </span>
          <button class="join-initiative-btn px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold border border-slate-900 transition-all text-xs focus:ring-2 focus:ring-slate-900 shadow-sm" data-id="${action.id}">
            Join Pod
          </button>
        </div>
      </div>
    `).join("");

    container.querySelectorAll(".join-initiative-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        btn.innerText = "✓ Enrolled!";
        btn.classList.add("bg-emerald-700", "text-white", "border-emerald-700");
        btn.classList.remove("bg-slate-900");
        App.showNotification("You have enrolled in this community clean-air action!");
      });
    });
  },

  async fetchReports() {
    const container = document.getElementById("community-incident-feed");
    if (!container) return;

    try {
      const res = await fetch("/api/community/reports");
      if (!res.ok) throw new Error("Could not fetch reports");
      const reports = await res.json();
      this.reports = reports;
      this.renderReports(reports);
    } catch (err) {
      console.error(err);
      this.renderReports(this.reports);
    }
  },

  renderReports(reports) {
    const container = document.getElementById("community-incident-feed");
    if (!container) return;

    if (!reports || reports.length === 0) {
      container.innerHTML = `<div class="text-xs text-slate-500 py-4 text-center">No open burning reports currently logged for this area.</div>`;
      return;
    }

    container.innerHTML = reports.map(r => `
      <div class="p-3.5 rounded-xl bg-white border border-slate-200 shadow-sm text-xs">
        <div class="flex items-center justify-between mb-1">
          <span class="font-bold text-red-700 flex items-center space-x-1">
            <span>🔥 ${r.type}</span>
          </span>
          <span class="text-[10px] text-slate-500 font-mono">${r.timestamp}</span>
        </div>
        <div class="text-slate-800 font-medium mb-1.5 flex items-center justify-between">
          <span>📍 ${r.location}</span>
          <span class="text-[10px] px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-semibold">${r.status}</span>
        </div>
        ${r.details ? `<p class="text-slate-600 text-[11px] mb-1 italic">"${r.details}"</p>` : ''}
        <div class="text-[10px] text-slate-400">Reported via ${r.reportedBy}</div>
      </div>
    `).join("");
  },

  setupReportForm() {
    const form = document.getElementById("smoke-report-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const city = App.getCurrentCity();
      const locInput = document.getElementById("report-location");
      const typeInput = document.getElementById("report-type");
      const detailsInput = document.getElementById("report-details");

      const payload = {
        cityKey: city.id,
        location: locInput?.value || "Neighborhood Intersection",
        incidentType: typeInput?.value || "Open Waste Burning",
        details: detailsInput?.value || "Thick black smoke drifting into residential area",
        photoAttached: false
      };

      try {
        const res = await fetch("/api/community/report-smoke", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Submission failed");
        const data = await res.json();
        
        App.showNotification(`Incident Ticket #${data.ticketId} dispatched to clean air rapid response squad!`);
        if (locInput) locInput.value = "";
        if (detailsInput) detailsInput.value = "";

        this.fetchReports();
      } catch (err) {
        console.error(err);
        App.showNotification("Incident recorded locally and added to community feed.");
        this.reports.unshift({
          id: `rep-local-${Date.now()}`,
          location: payload.location,
          city: payload.cityKey,
          type: payload.incidentType,
          timestamp: "Just now",
          severity: "High",
          status: "Logged by Citizen",
          details: payload.details,
          reportedBy: "You (Citizen Guardian)"
        });
        this.renderReports(this.reports);
      }
    });
  },

  setupPledges() {
    const pledgeBoxes = document.querySelectorAll(".clean-air-pledge-check");
    pledgeBoxes.forEach(box => {
      box.addEventListener("change", () => {
        const checkedCount = document.querySelectorAll(".clean-air-pledge-check:checked").length;
        const countDisplay = document.getElementById("pledge-count-display");
        if (countDisplay) {
          countDisplay.innerText = `${checkedCount} / ${pledgeBoxes.length} Pledges Active`;
        }
      });
    });
  }
};
