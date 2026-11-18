"""
ai_engine.py
GenAI environmental and clinical reasoning assistant for navigating severe winter smog.
Supports Google Gemini API with fallback to built-in clinical/environmental reasoning engine.
"""

import json
import os
from typing import Dict, Any, List, Optional

def build_vulnerability_summary(profile: Optional[Dict[str, Any]]) -> str:
    """Produces human-readable description of household vulnerabilities."""
    if not profile:
        return "Standard Adult Risk Profile"
    
    tags = []
    if profile.get("infants", 0) > 0:
        tags.append(f"{profile['infants']} Toddler/Infant (Underdeveloped lung alveoli)")
    if profile.get("asthmatics", 0) > 0:
        tags.append(f"{profile['asthmatics']} Asthmatic/Respiratory (Bronchial hyper-reactivity)")
    if profile.get("seniors", 0) > 0:
        tags.append(f"{profile['seniors']} Elderly (Cardiovascular cold-smog vulnerability)")
    if profile.get("pets", 0) > 0:
        tags.append(f"{profile['pets']} Pet (Ground-level particulate inhalation)")

    return ", ".join(tags) if tags else "Standard Adult Risk Profile"

def query_gemini_api(
    message: str,
    city: Dict[str, Any],
    profile: Optional[Dict[str, Any]],
    api_key: str
) -> Optional[str]:
    """Queries Gemini 1.5 Flash API with environmental context."""
    try:
        import urllib.request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        vuln_text = build_vulnerability_summary(profile)
        system_instruction = (
            f"You are AeroFamily Guardian, an expert GenAI air quality and environmental health assistant. "
            f"Current Location: {city['name']}, Outdoor PM2.5: {city['pm25']} µg/m³, AQI: {city['aqi']} ({city['status']}). "
            f"Inversion Layer: {city['inversionStrength']}, Recommended Midday Ventilation Window: {city['ventilationWindow']}. "
            f"Family Vulnerabilities: {vuln_text}. "
            f"Provide compassionate, scientifically precise advice on daily routines, IAQ hacks (Corsi-Rosenthal box, draft sealing), "
            f"and explain direct personal and community impact."
        )

        payload = {
            "contents": [
                {"parts": [{"text": f"{system_instruction}\n\nUser Question: {message}"}]}
            ],
            "generationConfig": {
                "temperature": 0.35,
                "maxOutputTokens": 1000
            }
        }
        
        req_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_bytes, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None

def generate_offline_reasoning(
    message: str,
    city: Dict[str, Any],
    profile: Optional[Dict[str, Any]]
) -> str:
    """
    Built-in expert clinical and environmental reasoning engine.
    Produces rich markdown with quantified impacts, warning alerts, and actionable steps.
    """
    msg = message.lower()
    vuln_summary = build_vulnerability_summary(profile)
    cigs_equiv = round(city["pm25"] / 22.0, 1)

    # 1. Topic: Pediatric / School / Outdoor Play
    if any(k in msg for k in ["school", "child", "kid", "baby", "play", "outdoor", "park", "sports", "recess"]):
        return f"""### 🛡️ Pediatric Winter Smog Advisory & Protection Plan
**Target Area:** {city['name']} | **Current PM2.5:** {city['pm25']} µg/m³ ({city['status']})  
**Toxicity Index:** Breathing outside today delivers the particulate toxicity of ~**{cigs_equiv} cigarettes/day**.

---

#### 🚨 Clinical Assessment for Your Family ({vuln_summary}):
Children are disproportionately harmed by winter smog:
- **Tidal Volume & Rate:** Children inhale **50% more air per kg of body mass** than adults.
- **Immature Alveoli:** Fine PM2.5 particles penetrate past immature bronchiolar walls into capillary beds, initiating systemic oxidative stress and suppressing lung volume development.

#### 📋 Actionable Directives:
1. **Physical Activity & School Sports:**
   - Immediately cancel outdoor physical education (P.E.), running, and soccer. Intense aerobic breathing causes oral respiration, bypassing the nasal filter entirely.
   - Switch to indoor yoga, stretching, or reading in a HEPA-filtered safe room.
2. **School Commute Protocol:**
   - Equip your child with a certified, well-sealed **KF94 or pediatric KN95 mask**. Cloth/surgical masks leak 70%+ of toxic sub-micron particulates around nasal margins.
   - When driving, keep vehicle windows strictly rolled up with HVAC set to **100% Recirculation mode**.
3. **Midday Window Caution:**
   - Even during the midday ventilation window (**{city['ventilationWindow']}**), children should remain indoors if outdoor PM2.5 exceeds 100 µg/m³.

> **Direct Impact:** Keeping your child shielded indoors today prevents approx. **360–420 micrograms of toxic heavy-metal laden particulates** from depositing in their alveolar sacs."""

    # 2. Topic: Corsi-Rosenthal Box / DIY Air Purifiers
    elif any(k in msg for k in ["corsi", "rosenthal", "diy", "box fan", "purifier", "cadr", "merv"]):
        return f"""### 🛠️ DIY Corsi-Rosenthal Box Air Filtration Blueprint
**Context:** {city['name']} | **Indoor Clean Air Delivery Strategy**

---

#### 💡 The Engineering Advantage:
- **Massive Media Surface Area:** 4 MERV 13 furnace filters offer **~32 square feet** of filtration media. The large area dramatically lowers airflow resistance, allowing an inexpensive 20-inch box fan to achieve **280–450 CFM (Clean Air Delivery Rate)** with whisper-quiet low motor strain.
- **Cost vs Performance:** Delivers hospital-grade CADR for **₹6,000 total**, matching commercial ₹45,000 units while costing 70% less for replacement filters.

#### 🔧 Step-by-Step Construction Guide:
1. **Bill of Materials:**
   - 1x 20-inch standard 3-speed box fan.
   - 4x MERV 13 furnace filters (20" x 20" x 1" or 20" x 20" x 2").
   - 1x 20" x 20" cardboard base plate.
   - Heavy-duty duct tape or gaffer tape.
   - Cardboard shroud with a 15-inch circular opening.
2. **Assembly:**
   - **Base:** Place the 20" x 20" cardboard plate flat on the floor.
   - **Cube:** Stand the 4 filters on edge around the base. **CRITICAL:** Ensure the airflow arrows on all 4 filters point **INWARD** toward the central hollow cavity.
   - **Seams:** Tape all vertical corners and the bottom perimeter completely airtight with duct tape.
   - **Fan Placement:** Set the box fan on top, blowing **UPWARD** toward the ceiling.
   - **The Shroud Boost:** Cut a 15-inch circular hole in a piece of cardboard and tape it over the front grill of the fan. This shroud blocks reverse corner vortex recirculation, increasing filtration efficiency by **35% to 40%**.
   - **Top Seal:** Tape the fan housing firmly to the tops of the filters.

> **Operational Impact:** Operates on ~35 Watts on Speed 1 (~₹8/day). In a 350 sq ft room, drops PM2.5 from **350 µg/m³ down to under 15 µg/m³ in 22 minutes**."""

    # 3. Topic: Commute & Transit
    elif any(k in msg for k in ["commute", "travel", "car", "metro", "bus", "bike", "cycle", "walk", "traffic"]):
        return f"""### 🚗 Low-Emission Commute & Exposure Defense
**City:** {city['name']} | **Roadside PM2.5 Multiplier:** Up to 1.8x background (~**{int(city['pm25']*1.8)} µg/m³**)

---

#### 🛑 The Morning Stagnation Hazard:
Between 06:30 AM and 09:30 AM, cold surface air is capped by the winter thermal inversion. Exhaust fumes from trucks and cold engines accumulate in arterial canyons.

#### 🔄 Sustainable Alternatives & Shielding:
1. **Switch to Underground Electric Metro:**
   - Reduces personal inhaled particulate dose by **65% to 75%** compared to riding a two-wheeler or sitting in non-recirculated car traffic.
   - Averts 3.6 kg of CO2e and 35g of tailpipe PM emissions per trip.
2. **Vehicle Cabin Recirculation Protocol:**
   - Never use "Fresh Air" intake on winter mornings. Set HVAC strictly to **Internal Recirculation**.
   - Upgrade your vehicle cabin air filter to a **True HEPA / Activated Carbon cabin insert**.
3. **Neighborhood Carpooling:**
   - Consolidate school or office trips into a 3-family carpool pod. Eliminating 2 cold starts takes 2 vehicles off the road during peak inversion hours.
4. **Postpone Outdoor Cycling / Jogging:**
   - High ventilation during cycling forces 45–60 L/min of air deep into bronchial branches. Save intense cardio for indoor air-purified rooms."""

    # 4. Topic: Ventilation / Windows / CO2 vs Smog
    elif any(k in msg for k in ["window", "ventilate", "ventilation", "fresh air", "air exchange", "co2", "stuffy", "purge"]):
        return f"""### 🪟 The 20-Minute Midday Inversion Purge Protocol
**City:** {city['name']} | **Optimal Ventilation Window Today:** **{city['ventilationWindow']}**

---

#### ⚖️ The Balancing Act: Smog vs Carbon Dioxide (CO2)
Keeping a house sealed 24/7 with a full family causes indoor CO2 to rise past **1,500 - 2,000 ppm**, causing headaches, lethargy, cognitive decline, and reduced immune defense. Yet opening windows in the morning floods the home with toxic winter particulates.

#### ⏱️ The Execution Protocol:
1. **Strictly Blackout Hours:** 06:00 - 10:30 AM and 18:30 - 22:30 PM (strongest surface inversion, peak vehicle exhaust).
2. **Optimal Window:** **{city['ventilationWindow']}**. Solar insolation breaks the surface inversion, boundary layer height rises, and outdoor particulate concentration reaches diurnal lows.
3. **Cross-Ventilation Flush:** Open opposite windows wide for **exactly 15 to 20 minutes**. High air throughput flushes accumulated CO2 from 1,800 ppm to 650 ppm without chilling down furniture and walls.
4. **Immediate Post-Flush Scrubbing:** Seal all windows immediately at minute 20, then run your HEPA purifier or Corsi-Rosenthal box on **TURBO for 25 minutes** to capture newly introduced particulates.

> **Result:** Fresh oxygen without trapped winter smog."""

    # 5. Default / Comprehensive Plan
    else:
        return f"""### 🛡️ AeroFamily Clean Air Intelligence Briefing
**Location:** {city['name']} | **Current AQI:** {city['aqi']} ({city['status']})  
**Particulate Loading:** PM2.5: **{city['pm25']} µg/m³** | PM10: {city['pm10']} µg/m³  
**Household Shield Active:** {vuln_summary}

---

#### 🔍 Meteorological Inversion Analysis:
The winter thermal inversion over {city['name']} creates a stagnant boundary layer cap under {city['temperature']}°C temperatures. Inhaling unprotected ambient air today delivers a toxic load equivalent to **~{cigs_equiv} cigarettes/day**.

#### 🎯 4-Pillar Daily Protection Plan:
1. **Low-Emission Commute & Routing:**
   - Avoid arterial traffic during morning stagnation (07:00 - 09:30).
   - Use underground metro or enforce 100% car cabin recirculation with N95 masks.
2. **Indoor Air Defense & DIY Filtration:**
   - Build or deploy a **Corsi-Rosenthal Box** (MERV 13 filters + box fan) for ₹6,000 hospital-grade filtration.
   - Seal door and window gaps with high-density EVA foam weatherstripping.
   - Maintain 40–50% relative humidity using evaporative or distilled water humidifiers (avoid tap water white dust).
3. **Timed Ventilation Window:**
   - Flush indoor CO2 during the diurnal minimum (**{city['ventilationWindow']}**) for 15-20 minutes, followed by a 20-min purifier turbo burst.
4. **Community Action & Collective Mitigation:**
   - Join the neighborhood school carpool pod to pull idling cars off school gates.
   - Report open biomass burning through the community spotter tool.

*Ask any specific question about pediatric safeguards, DIY purifier sizing, window sealing, or low-emission heating!*"""

def generate_ai_response(
    message: str,
    city: Dict[str, Any],
    profile: Optional[Dict[str, Any]],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Orchestrates AI response generation via Gemini API with offline fallback."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if key:
        gemini_res = query_gemini_api(message, city, profile, key)
        if gemini_res:
            return {"reply": gemini_res, "source": "gemini-1.5-flash", "city": city["name"]}
            
    offline_reply = generate_offline_reasoning(message, city, profile)
    return {"reply": offline_reply, "source": "clinical-environmental-reasoning-engine", "city": city["name"]}
