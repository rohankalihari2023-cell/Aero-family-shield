"""
ai_engine.py
GenAI environmental and clinical reasoning assistant for navigating severe winter smog.
Provides multi-turn conversational advisory grounded in real-time meteorology,
inversion physics, and personalized household vulnerability profiles.
Supports Google Gemini 1.5 Flash API with deterministic clinical fallback.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from core.config import get_logger

logger = get_logger(__name__)


def build_vulnerability_summary(profile: Optional[Dict[str, Any]]) -> str:
    """Produces a human-readable clinical summary of household vulnerabilities for AI prompts.

    Args:
        profile (Optional[Dict[str, Any]]): Demographic dictionary with counts of vulnerable members.

    Returns:
        str: Formatted string describing active clinical sensitivities, or 'Standard Adult Risk Profile'.

    Example:
        >>> build_vulnerability_summary({"infants": 1, "asthmatics": 1})
        '1 Toddler/Infant (Underdeveloped lung alveoli), 1 Asthmatic/Respiratory (Bronchial hyper-reactivity)'
    """
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
    """Queries the Google Gemini 1.5 Flash API with rich environmental and clinical context.

    Args:
        message (str): User prompt or question.
        city (Dict[str, Any]): Active city meteorological data including PM2.5, AQI, and inversion depth.
        profile (Optional[Dict[str, Any]]): Household vulnerability profile.
        api_key (str): Google Gemini API key.

    Returns:
        Optional[str]: Generated markdown response from Gemini, or None if the call fails.
    """
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        vuln_text = build_vulnerability_summary(profile)
        system_instruction = (
            f"You are AeroFamily Guardian, an expert GenAI air quality and environmental health assistant. "
            f"Current Location: {city.get('name', 'Local')}, Outdoor PM2.5: {city.get('pm25', 100)} µg/m³, "
            f"AQI: {city.get('aqi', 150)} ({city.get('status', 'Unhealthy')}). "
            f"Inversion Layer: {city.get('inversionStrength', 'Active')}, "
            f"Recommended Midday Ventilation Window: {city.get('ventilationWindow', '12:30 PM - 2:30 PM')}. "
            f"Family Vulnerabilities: {vuln_text}. "
            f"Provide compassionate, scientifically precise advice on daily routines, IAQ hacks (Corsi-Rosenthal box, draft sealing), "
            f"and explain direct personal and community impact in Indian Rupees (₹)."
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
        req = urllib.request.Request(
            url,
            data=req_bytes,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            candidates = res_json.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"]
            return None

    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as err:
        logger.warning("Gemini API call failed (%s). Falling back to clinical reasoning engine.", str(err))
        return None
    except Exception as err:
        logger.error("Unexpected error in query_gemini_api: %s", str(err), exc_info=True)
        return None


def generate_offline_reasoning(
    message: str,
    city: Dict[str, Any],
    profile: Optional[Dict[str, Any]]
) -> str:
    """Built-in clinical and environmental reasoning engine.

    Provides deterministic, science-backed guidance when Gemini is offline or API key is absent.

    Args:
        message (str): User inquiry text.
        city (Dict[str, Any]): Active city record with meteorological indicators.
        profile (Optional[Dict[str, Any]]): Active household profile.

    Returns:
        str: Comprehensive, formatted markdown guidance tailored to the inquiry.
    """
    msg = message.lower()
    vuln_summary = build_vulnerability_summary(profile)
    cigs_equiv = round(city.get("pm25", 100.0) / 22.0, 1)

    # 1. Topic: Pediatric / School / Outdoor Play
    if any(k in msg for k in ["school", "child", "kid", "baby", "play", "outdoor", "park", "sports", "recess"]):
        return f"""### 🛡️ Pediatric Winter Smog Advisory & Protection Plan
**Target Area:** {city['name']} | **Current PM2.5:** {city['pm25']} µg/m³ ({city['status']})  
**Toxicity Index:** Breathing outside today delivers the particulate toxicity of ~**{cigs_equiv} cigarettes/day**.

---

#### 🚨 Clinical Assessment for Your Family ({vuln_summary}):
Children are disproportionately harmed by winter smog:
- **Tidal Volume & Rate:** Children inhale **50% more air per kg of body mass** than adults.
- **Lung Architecture:** Alveolar proliferation continues until age 8; fine particles (PM2.5) permanently stunt airway caliber.
- **Near-Ground Microclimate:** Heavier diesel soot concentrates within 1 meter of ground level where young children walk and play.

#### 💡 Actionable Pediatric Protocol:
1. **Cancel Strenuous Outdoor Recess:** Move physical activities indoors. Aerobic exercise triples minute ventilation, driving micro-dust deep into bronchioles.
2. **Pediatric Mask Fit:** Standard adult masks leave massive edge leak gaps (>40%). Use child-specific **KF94 or KN95 Small** masks with an adjustable nose wire.
3. **Midday Green Window:** If outdoor play is unavoidable, restrict it strictly to **{city['ventilationWindow']}** when solar heating temporarily breaks the thermal stagnation cap.

> **Direct Impact:** Shifting a 45-minute outdoor sports practice indoors prevents **~95 µg of toxic particulate deposition** in your child's alveolar sacs today."""

    # 2. Topic: DIY Air Purifiers / Corsi-Rosenthal Box
    elif any(k in msg for k in ["purifier", "filter", "c-r", "corsi", "box fan", "diy", "hepa", "cost", "cleaner"]):
        return f"""### 🔬 DIY Corsi-Rosenthal (C-R) Box Engineering Guide
**Status:** Highly Recommended Alternative for {city['name']} during Severe Winter Smog.

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
Between 07:00 and 09:30 AM, cold nocturnal boundary layers suppress vehicular tailpipe exhaust directly at street level. 

#### 🛡️ Low-Exposure Commute Hierarchy:
1. **Gold Standard — Underground Electric Metro:**
   - Deep underground stations avoid the surface inversion layer.
   - Eliminates personal driving emissions entirely (**-2.1 kg CO2e/trip**).
2. **Silver Standard — School/Work Carpool Pod:**
   - Cuts neighborhood vehicular cold-starts.
   - Keep car windows strictly closed; set HVAC to **100% Recirculation** mode (cuts in-cabin PM2.5 by 80% within 4 minutes).
3. **High Risk — Open Two-Wheelers / Walking along Arterials:**
   - Inhales raw diesel soot and tire wear microplastics.
   - Mandatory: Wear a well-fitted **N95/FFP2 respirator**. Simple cloth or surgical masks leak >60% of ultra-fine particles along the sides."""

    # 4. Topic: Natural Ventilation & Opening Windows
    elif any(k in msg for k in ["window", "ventilate", "ventilation", "fresh air", "air out", "smell", "co2"]):
        return f"""### 💨 Strategic Winter Inversion Ventilation Protocol
**City:** {city['name']} | **Optimal Daily Window:** **{city['ventilationWindow']}**

---

#### 🛑 The Winter Inversion Paradox:
Sealing your home prevents outdoor smog from entering, but human exhalation causes indoor CO2 to climb past **1,800 ppm**, inducing headaches, brain fog, and poor sleep. Opening windows at the wrong time floods the house with toxic particulate soot.

#### ⏱️ The 20-Minute Convective Purge Protocol:
1. **Never Ventilate at Night or Early Morning:** Between 06:00–10:00 AM and 19:00–23:00 PM, cold boundary layer compression traps maximum pollution.
2. **Ventilate at the Midday Diurnal Peak ({city['ventilationWindow']}):** Solar thermal heating breaks the ground inversion, wind speeds pick up, and pollution hits its lowest 24-hr concentration.
3. **Cross-Draft Purge:** Open opposite windows wide for exactly **15 to 20 minutes** to rapidly replace stale room air.
4. **Immediate Reseal & Turbo Clean:** Seal all windows and run your air purifier on Turbo/High for 30 minutes to scrub any entered particulates back to sub-15 µg/m³."""

    # 5. Default General Guidance
    return f"""### 🛡️ AeroFamily Guardian Advisory for {city['name']}
**Current Ambient Conditions:** PM2.5: **{city['pm25']} µg/m³** ({city['status']}) | AQI: **{city['aqi']}**  
**Active Inversion Layer:** {city['inversionStrength']}  
**Configured Family Profile:** {vuln_summary}

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
    """Orchestrates AI response generation using Gemini with automatic clinical fallback.

    Args:
        message (str): User inquiry string.
        city (Dict[str, Any]): Active city environmental record.
        profile (Optional[Dict[str, Any]]): Active household profile.
        api_key (Optional[str], optional): Optional API key override.

    Returns:
        Dict[str, Any]: Response payload containing 'reply', 'source', and 'city'.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if key:
        gemini_res = query_gemini_api(message, city, profile, key)
        if gemini_res:
            return {"reply": gemini_res, "source": "gemini-1.5-flash", "city": city.get("name", "Local")}

    offline_reply = generate_offline_reasoning(message, city, profile)
    return {
        "reply": offline_reply,
        "source": "clinical-environmental-reasoning-engine",
        "city": city.get("name", "Local")
    }
