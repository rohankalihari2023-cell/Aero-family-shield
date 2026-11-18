/**
 * @file ai-advisor.js
 * @description GenAI Clean Air Assistant Module.
 * Facilitates multi-turn contextual dialog, client-side Markdown parsing,
 * clinical vulnerability awareness, and quick guidance prompts.
 */
"use strict";

const AIAdvisor = {
  chatHistory: [],
  isGenerating: false,

  quickPrompts: [
    { label: "👶 Child outdoor play today?", prompt: "Is it safe for my child to play outdoors today, and how should we handle school PE and the school commute?" },
    { label: "🛠️ DIY Corsi-Rosenthal Box", prompt: "How do I build a DIY Corsi-Rosenthal box purifier with box fans and MERV 13 filters on a budget?" },
    { label: "🪟 Inversion ventilation window", prompt: "When is the safest ventilation window today to flush indoor CO2 without letting winter smog in?" },
    { label: "🚗 Low-emission commute shift", prompt: "What is the best low-emission commute alternative for our family today to minimize PM2.5 inhalation?" },
    { label: "💨 Humidifier white dust danger", prompt: "Is it true that ultrasonic humidifiers create dangerous PM2.5 white dust with tap water?" },
    { label: "🔥 Clean heating vs wood fire", prompt: "What are clean, low-emission heating hacks for our home during this severe winter smog?" }
  ],

  init() {
    this.renderInitialMessage();
    this.renderQuickPills();
    this.setupEventListeners();
  },

  renderQuickPills() {
    const container = document.getElementById("ai-quick-pills");
    if (!container) return;
    
    container.innerHTML = this.quickPrompts.map(qp => `
      <button class="quick-pill text-xs font-semibold px-3 py-1.5 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 hover:border-slate-500 transition-all flex items-center space-x-1.5 whitespace-nowrap focus:ring-2 focus:ring-slate-900" data-prompt="${qp.prompt.replace(/"/g, '&quot;')}">
        <span>${qp.label}</span>
      </button>
    `).join("");

    container.querySelectorAll(".quick-pill").forEach(btn => {
      btn.addEventListener("click", () => {
        const prompt = btn.getAttribute("data-prompt");
        const input = document.getElementById("ai-chat-input");
        if (input) {
          input.value = prompt;
          this.sendMessage();
        }
      });
    });
  },

  renderInitialMessage() {
    const city = App.getCurrentCity();
    const profile = App.getFamilyProfile();
    const hasVuln = profile.infants > 0 || profile.asthmatics > 0 || profile.seniors > 0 || profile.pets > 0;
    
    const welcomeHtml = `
      <div class="chat-message flex items-start space-x-3 mb-4">
        <div class="w-9 h-9 rounded-xl bg-slate-900 text-white font-bold flex items-center justify-center shrink-0 text-sm shadow-sm" aria-hidden="true">
          AERO
        </div>
        <div class="chat-bubble-ai p-4 rounded-2xl max-w-[85%] text-slate-800 text-sm leading-relaxed bg-white border border-slate-200 shadow-sm">
          <div class="flex items-center space-x-2 mb-2">
            <span class="font-bold text-slate-950">AeroFamily AI Guardian</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-300 font-mono">Smog Intelligence Engine</span>
          </div>
          <p class="mb-2">
            Hello! I am your clean air & winter smog copilot. I monitor localized temperature inversions, PM2.5 particulate loading, and toxic diurnal spikes for <strong>${city.name}</strong>.
          </p>
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 mb-2">
            <div class="flex items-center space-x-2 text-amber-800 font-semibold mb-1">
              <span>⚠️ Current Risk Alert: ${city.status} (PM2.5: ${city.pm25} µg/m³)</span>
            </div>
            <div>${city.advisory}</div>
            ${hasVuln ? `<div class="mt-1.5 text-slate-950 font-bold">🛡️ Configured family safeguards active: ${App.getVulnerabilitySummary()}</div>` : ''}
          </div>
          <p class="text-xs text-slate-500">
            Ask me anything about daily routines, DIY purifiers, indoor sealing, child safety, or click any quick topic below!
          </p>
        </div>
      </div>
    `;

    const chatContainer = document.getElementById("ai-chat-messages");
    if (chatContainer) {
      chatContainer.innerHTML = welcomeHtml;
    }
  },

  setupEventListeners() {
    const form = document.getElementById("ai-chat-form");
    const input = document.getElementById("ai-chat-input");
    
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.sendMessage();
      });
    }

    if (input) {
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }

    const clearBtn = document.getElementById("clear-chat-btn");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        this.chatHistory = [];
        this.renderInitialMessage();
      });
    }

    // API Key toggle modal
    const saveKeyBtn = document.getElementById("save-api-key-btn");
    if (saveKeyBtn) {
      saveKeyBtn.addEventListener("click", () => {
        const keyInput = document.getElementById("gemini-api-key-input");
        if (keyInput) {
          localStorage.setItem("aerofamily_gemini_key", keyInput.value.trim());
          App.showNotification("Gemini API key saved successfully!");
        }
      });
    }
  },

  async sendMessage() {
    const input = document.getElementById("ai-chat-input");
    if (!input || this.isGenerating) return;

    const message = input.value.trim();
    if (!message) return;

    input.value = "";
    this.isGenerating = true;

    // Append User Message to UI
    this.appendUserMessage(message);
    this.chatHistory.push({ role: "user", text: message });

    // Show Typing Indicator
    const typingId = this.showTypingIndicator();

    try {
      const city = App.getCurrentCity();
      const profile = App.getFamilyProfile();
      const customKey = localStorage.getItem("aerofamily_gemini_key") || "";

      const response = await fetch("/api/advisor/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message,
          cityKey: city.id,
          familyProfile: profile,
          apiKey: customKey
        })
      });

      this.removeTypingIndicator(typingId);

      if (!response.ok) {
        throw new Error("Failed to receive response from server");
      }

      const data = await response.json();
      this.appendAIMessage(data.reply, data.source);
      this.chatHistory.push({ role: "model", text: data.reply });

    } catch (err) {
      console.error(err);
      this.removeTypingIndicator(typingId);
      
      // Fallback local response if network issue
      const city = App.getCurrentCity();
      const localReply = this.generateFallbackResponse(message, city);
      this.appendAIMessage(localReply, "offline-knowledge-base");
      this.chatHistory.push({ role: "model", text: localReply });
    } finally {
      this.isGenerating = false;
      const chatContainer = document.getElementById("ai-chat-messages");
      if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  },

  appendUserMessage(text) {
    const container = document.getElementById("ai-chat-messages");
    if (!container) return;

    const div = document.createElement("div");
    div.className = "chat-message flex items-start justify-end space-x-3 mb-4";
    div.innerHTML = `
      <div class="chat-bubble-user p-3.5 rounded-2xl max-w-[80%] text-white text-sm leading-relaxed shadow-sm font-medium bg-slate-900">
        ${escapeHtml(text)}
      </div>
      <div class="w-9 h-9 rounded-xl bg-slate-200 border border-slate-300 flex items-center justify-center text-slate-900 font-bold shrink-0 text-xs">
        YOU
      </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  },

  appendAIMessage(markdownText, source) {
    const container = document.getElementById("ai-chat-messages");
    if (!container) return;

    const parsedHtml = this.parseSimpleMarkdown(markdownText);
    const sourceBadge = source === "gemini-1.5-flash" ? "Gemini 1.5 Flash" : "Smog Knowledge Base";

    const div = document.createElement("div");
    div.className = "chat-message flex items-start space-x-3 mb-4";
    div.innerHTML = `
      <div class="w-9 h-9 rounded-xl bg-slate-900 text-white font-bold flex items-center justify-center shrink-0 text-sm shadow-sm">
        AERO
      </div>
      <div class="chat-bubble-ai p-4 rounded-2xl max-w-[85%] text-slate-800 text-sm leading-relaxed bg-white border border-slate-200 shadow-sm ai-prose">
        <div class="flex items-center justify-between mb-2 pb-1.5 border-b border-slate-200">
          <div class="flex items-center space-x-2">
            <span class="font-bold text-slate-950">AeroFamily AI Guardian</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-300 font-mono">${sourceBadge}</span>
          </div>
          <button class="copy-msg-btn text-xs text-slate-500 hover:text-slate-900 transition-colors focus:ring-1 focus:ring-slate-900 rounded px-1.5 py-0.5" title="Copy response">
            📋 Copy
          </button>
        </div>
        <div class="ai-content">${parsedHtml}</div>
      </div>
    `;

    const copyBtn = div.querySelector(".copy-msg-btn");
    if (copyBtn) {
      copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(markdownText);
        copyBtn.innerText = "✓ Copied!";
        setTimeout(() => copyBtn.innerText = "📋 Copy", 2000);
      });
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  },

  showTypingIndicator() {
    const container = document.getElementById("ai-chat-messages");
    if (!container) return null;

    const id = "typing-" + Date.now();
    const div = document.createElement("div");
    div.id = id;
    div.className = "chat-message flex items-start space-x-3 mb-4";
    div.innerHTML = `
      <div class="w-9 h-9 rounded-xl bg-slate-900 text-white font-bold flex items-center justify-center shrink-0 text-sm">
        AERO
      </div>
      <div class="chat-bubble-ai px-4 py-3 rounded-2xl text-slate-700 text-sm bg-white border border-slate-200 shadow-sm flex items-center space-x-2">
        <div class="flex space-x-1">
          <div class="w-2 h-2 rounded-full bg-slate-900 animate-bounce" style="animation-delay: 0ms"></div>
          <div class="w-2 h-2 rounded-full bg-slate-900 animate-bounce" style="animation-delay: 150ms"></div>
          <div class="w-2 h-2 rounded-full bg-slate-900 animate-bounce" style="animation-delay: 300ms"></div>
        </div>
        <span class="text-xs text-slate-500">Analyzing atmospheric inversion & exposure model...</span>
      </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
  },

  removeTypingIndicator(id) {
    if (!id) return;
    const elem = document.getElementById(id);
    if (elem) elem.remove();
  },

  parseSimpleMarkdown(text) {
    if (!text) return "";
    let html = text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 bg-slate-100 rounded text-slate-900 text-xs border border-slate-300 font-mono font-semibold">$1</code>')
      .replace(/^---$/gim, '<hr/>');

    // Lists
    html = html.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\s*\d+\.\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
    
    // Line breaks to paragraphs
    const paragraphs = html.split(/\n\n+/);
    html = paragraphs.map(p => {
      p = p.trim();
      if (!p) return "";
      if (p.startsWith('<h') || p.startsWith('<ul') || p.startsWith('<blockquote') || p.startsWith('<hr')) {
        return p;
      }
      return `<p>${p.replace(/\n/g, '<br/>')}</p>`;
    }).join("");

    return html;
  },

  generateFallbackResponse(msg, city) {
    return `### 🛡️ AeroFamily Emergency Smog Guidance
**Location:** ${city.name} | **Current PM2.5:** ${city.pm25} µg/m³ (${city.status})

---
- **Airway Defense:** In winter inversions, cold ground air traps tailpipe soot and biomass smoke. Keep windows sealed, run a HEPA or Corsi-Rosenthal box, and wear a well-fitted N95/KF94 mask for any outdoor transit.
- **Midday Window:** Avoid early morning (6:30 - 9:30 AM) ventilation; purge indoor CO2 only during the solar inversion break (${city.ventilationWindow}) for 15-20 minutes.
- **Commute:** Shift to carpooling or underground metro, and set vehicle HVAC to 100% Recirculation mode.`;
  }
};

function escapeHtml(string) {
  const entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };
  return String(string).replace(/[&<>"']/g, s => entityMap[s]);
}
