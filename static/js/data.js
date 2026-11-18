/**
 * @file data.js
 * @description Static Smog & Clean Air Intelligence Knowledge Base.
 * Houses offline hotspot records, WHO 2021 air quality benchmarks,
 * IAQ engineering hack specifications, and community initiatives.
 */
"use strict";

const AERO_DATA = {
  cities: {
    delhi: {
      name: "Delhi NCR, India",
      country: "India",
      aqi: 418,
      status: "Severe / Hazardous",
      category: "hazardous",
      pm25: 342,
      pm10: 486,
      no2: 74,
      co: 2.8,
      temperature: 15,
      humidity: 68,
      inversionStrength: "High (Surface Inversion 80m)",
      windSpeed: "3.2 km/h (Stagnant Calm)",
      ventilationWindow: "12:30 PM - 2:30 PM",
      grapStage: "Stage IV (Severe+ Emergency)",
      dominantSources: ["Vehicular exhaust", "Stubble burning smoke transport", "Road/construction dust", "Secondary particulate formation in cold fog"],
      advisory: "Hazardous winter inversion trapping toxic micro-particulates at ground level. Avoid all unessential outdoor physical activities. Keep indoor HEPA systems running."
    },
    lahore: {
      name: "Lahore, Pakistan",
      country: "Pakistan",
      aqi: 435,
      status: "Hazardous Crisis",
      category: "hazardous",
      pm25: 388,
      pm10: 520,
      no2: 82,
      co: 3.1,
      temperature: 14,
      humidity: 72,
      inversionStrength: "Extreme (Mixing Layer <70m)",
      windSpeed: "2.8 km/h (Calm)",
      ventilationWindow: "1:00 PM - 2:30 PM",
      grapStage: "Green Lockdown / Smog Emergency",
      dominantSources: ["Low-grade fuel combustion", "Brick kilns without zigzag tech", "Transboundary smoke", "Cold winter fog condensation"],
      advisory: "Dense winter smog blanket with zero nocturnal dispersal. Vulnerable individuals (children, asthmatics, elderly) must strictly stay indoors with sealed windows."
    },
    beijing: {
      name: "Beijing, China",
      country: "China",
      aqi: 172,
      status: "Unhealthy",
      category: "unhealthy",
      pm25: 98,
      pm10: 165,
      no2: 44,
      co: 1.4,
      temperature: 2,
      humidity: 42,
      inversionStrength: "Moderate (Valley Orographic Trapping)",
      windSpeed: "6.5 km/h",
      ventilationWindow: "11:30 AM - 3:00 PM",
      grapStage: "Orange Air Alert",
      dominantSources: ["Winter centralized coal & gas heating", "Regional industrial haze from Hebei", "Automotive diesel corridors"],
      advisory: "Typical Northern China winter heating smog. Wear KN95/FFP2 outdoors and stagger commute hours away from morning stagnation."
    },
    saltlake: {
      name: "Salt Lake City, UT, USA",
      country: "United States",
      aqi: 148,
      status: "Unhealthy for Sensitive Groups",
      category: "sensitive",
      pm25: 56,
      pm10: 84,
      no2: 32,
      co: 0.9,
      temperature: -2,
      humidity: 58,
      inversionStrength: "Strong (Wasatch Basin Thermal Cap)",
      windSpeed: "4.1 km/h",
      ventilationWindow: "1:30 PM - 3:30 PM",
      grapStage: "Mandatory No-Burn Action Day",
      dominantSources: ["Great Basin winter temperature inversion", "Residential woodstoves", "Mobile emissions in trapped valley cold pool"],
      advisory: "Cold valley pool holding vehicle exhaust beneath warm mountain lid. Limit prolonged outdoor workouts and avoid all wood burning."
    },
    ulaanbaatar: {
      name: "Ulaanbaatar, Mongolia",
      country: "Mongolia",
      aqi: 365,
      status: "Hazardous Winter Peak",
      category: "hazardous",
      pm25: 315,
      pm10: 440,
      no2: 66,
      co: 3.5,
      temperature: -19,
      humidity: 74,
      inversionStrength: "Severe (Siberian High Anticyclone)",
      windSpeed: "2.1 km/h",
      ventilationWindow: "1:00 PM - 2:00 PM (Brief)",
      grapStage: "Winter Emergency Plan",
      dominantSources: ["Ger district raw coal & briquette stoves", "Low thermal insulation of housing", "Extreme cold-induced inversion"],
      advisory: "Extreme sub-zero inversion. Thick coal smoke hanging in Tuul River basin. Maximize internal air filtration and use thermal draft curtains."
    },
    katowice: {
      name: "Katowice / Silesia, Poland",
      country: "Poland",
      aqi: 168,
      status: "Unhealthy",
      category: "unhealthy",
      pm25: 88,
      pm10: 142,
      no2: 38,
      co: 1.2,
      temperature: 1,
      humidity: 82,
      inversionStrength: "Moderate (Foggy Valley Stagnation)",
      windSpeed: "5.0 km/h",
      ventilationWindow: "12:00 PM - 2:30 PM",
      grapStage: "Smog Alert Level 2",
      dominantSources: ["Old residential coal/wood boilers ('Kopciuchy')", "Low-stack domestic emissions", "Cold damp atmospheric stagnation"],
      advisory: "Elevated benzo(a)pyrene and PM2.5 from domestic heating. Seal window leaks and switch from fireplace to electric/heat pump where possible."
    },
    milan: {
      name: "Milan / Po Valley, Italy",
      country: "Italy",
      aqi: 154,
      status: "Unhealthy",
      category: "unhealthy",
      pm25: 62,
      pm10: 89,
      no2: 48,
      co: 1.1,
      temperature: 5,
      humidity: 79,
      inversionStrength: "Persistent (Po Basin Topographic Trap)",
      windSpeed: "3.0 km/h",
      ventilationWindow: "1:00 PM - 3:30 PM",
      grapStage: "Anti-Smog Traffic Restrictions",
      dominantSources: ["Dense diesel road transport", "Intensive agriculture ammonia reacting to fine PM", "Stagnant Alpine foothills basin"],
      advisory: "Winter microclimate trapping particulates in Lombardy basin. Shift to public transit and postpone outdoor jogging to mid-afternoon."
    }
  },

  whoGuidelines: {
    pm25_24h: 15, // µg/m3 (WHO Air Quality Guideline 2021)
    pm10_24h: 45, // µg/m3
    no2_24h: 25,  // µg/m3
    cigaretteFactor: 22 // 22 µg/m3 of 24h PM2.5 exposure ~ 1 cigarette (Berkeley Earth model)
  },

  familyVulnerabilities: {
    infant: {
      label: "Infant / Toddler (0-5 yrs)",
      icon: "baby",
      riskMultiplier: 2.8,
      notes: "Immature lung alveoli, breathes 2x faster per kg than adults, closer to ground-level road exhaust."
    },
    asthma: {
      label: "Asthmatic / Respiratory Condition",
      icon: "activity",
      riskMultiplier: 3.2,
      notes: "Severe airway hyper-responsiveness. Inhaled PM2.5 triggers bronchospasms, requires zero-ozone filtration."
    },
    elderly: {
      label: "Elderly Family Member (65+)",
      icon: "user-check",
      riskMultiplier: 2.5,
      notes: "Vulnerable to cardiovascular strain, blood pressure spikes, and cold-air induced microvascular constriction."
    },
    pet: {
      label: "Household Pets (Dogs/Cats/Birds)",
      icon: "heart",
      riskMultiplier: 1.9,
      notes: "Birds are ultra-sensitive to toxic aerosol; dogs walk at exhaust pipe level (15-30cm off tarmac)."
    },
    healthy: {
      label: "Healthy Adult / Outdoor Commuter",
      icon: "user",
      riskMultiplier: 1.0,
      notes: "Prolonged exposure still causes systemic microvascular inflammation and reduces aerobic capacity."
    }
  },

  iaqHacks: [
    {
      id: "corsi-rosenthal",
      title: "DIY Corsi-Rosenthal Clean Air Box",
      difficulty: "Easy (30 mins)",
      cost: "~₹5,000 - ₹6,500 (vs ₹28,000 - ₹50,000 commercial HEPA)",
      cadRate: "250 - 450 CFM (Clean Air Delivery Rate)",
      effectiveness: "Removes up to 90-95% of airborne PM2.5 and viral aerosol in a 400 sq ft room within 20 minutes.",
      materials: [
        "1x 20-inch standard box fan (3-speed)",
        "4x MERV 13 furnace filters (20x20x1 or 20x20x2 inches)",
        "1x 20x20 inch cardboard bottom base",
        "Duct tape or Gorilla tape (heavy duty)",
        "1x Circular cardboard shroud cutout (14-16 inch diameter opening on front face to prevent air recirculating back to fan corners)"
      ],
      steps: [
        "Place the cardboard square base flat on the floor.",
        "Arrange the 4 MERV 13 filters in a cube standing upright, with airflow arrows pointing INWARD toward the center.",
        "Tape the vertical seams firmly with duct tape on both inside and outside.",
        "Place the 20-inch box fan on top, pointing airflow UPWARD toward the ceiling.",
        "Cut a 15-inch circular hole in a cardboard piece and tape it onto the fan's face (the shroud boost increases airflow efficiency by 40%).",
        "Tape all perimeter joints airtight. Turn on fan to Speed 1 or 2 for whisper-quiet continuous filtration."
      ],
      proTips: "Running on Speed 1 uses only 35 Watts (approx. ₹8/day) and delivers cleaner air than many premium single-filter purifiers because of the massive filter surface area (over 30 sq ft)."
    },
    {
      id: "draft-sealing",
      title: "Thermal Draft Exclusion & Smog Barrier",
      difficulty: "Very Easy (15 mins)",
      cost: "₹400 - ₹1,200",
      cadRate: "Reduces outdoor smog infiltration by 45-65%",
      effectiveness: "Prevents toxic winter chimney effects and cold air leaks that suck outdoor smog through window sashes.",
      materials: [
        "Self-adhesive high-density EVA foam weatherstripping tape",
        "DIY Door Snake (old thick towel or long socks filled with dry rice/lentils or foam pipe insulation)",
        "Removable clear plastic window shrink film / bubble wrap for single pane glass"
      ],
      steps: [
        "Perform the 'Incense / Lighter Flame Test' along window frames on a windy cold evening to spot air drafts.",
        "Clean the window frame with rubbing alcohol and apply EVA foam tape along the contact rebate.",
        "Place the DIY Door Snake tightly against external door bottoms, especially apartment main doors opening to common hallways.",
        "For drafty single-pane windows, apply plastic cling film with double-sided tape and warm lightly with a hair dryer to create a thermal insulating air pocket."
      ],
      proTips: "A sealed room allows your air purifier to reach sub-15 µg/m³ PM2.5 up to 3x faster, while cutting space heating bills by 18%."
    },
    {
      id: "humidity-control",
      title: "Optimal Humidity & Ultrasonic Dust Prevention",
      difficulty: "Easy",
      cost: "₹0 - ₹2,000",
      cadRate: "Optimizes mucosal barrier & suppresses particle suspension",
      effectiveness: "Keeps respiratory cilia active and prevents dangerous aerosolization of tap water minerals as synthetic PM2.5.",
      materials: [
        "Hygrometer (aim for 40% - 50% relative humidity)",
        "Evaporative wick humidifier OR distilled / reverse osmosis water for ultrasonic units",
        "Stovetop simmering pot with orange peels/cinnamon (natural evaporative method)"
      ],
      steps: [
        "CRITICAL CAUTION: Never put hard tap water into an ultrasonic cool mist humidifier! The ultrasonic disc shatters mineral salts (calcium, magnesium) into fine particles <2.5µm, often spiking indoor PM2.5 readings to 300+ µg/m³ of mineral lung irritants.",
        "Use distilled or RO water in ultrasonic units, or switch to an evaporative wick humidifier (which naturally traps minerals in the wick).",
        "Maintain indoor humidity strictly between 40% and 50%. Below 30% dries nasal mucous membranes and leaves airways vulnerable; above 55% encourages dust mites and winter window condensation mold.",
        "Simple zero-cost hack: Hang freshly washed damp laundry indoors or place shallow bowls of water near warm radiators."
      ],
      proTips: "At 45% relative humidity, airborne PM2.5 particles absorb trace water molecules, agglomerate into heavier clusters, and settle onto floors where they can be damp-mopped."
    },
    {
      id: "wet-cleaning",
      title: "Damp Microfiber Cleansing Protocol",
      difficulty: "Very Easy",
      cost: "₹250",
      cadRate: "Prevents 85% particulate resuspension",
      effectiveness: "Eliminates settled fine dust without launching PM2.5 back into the breathing zone.",
      materials: [
        "Damp microfiber cloths",
        "Microfiber flat floor mop",
        "Diluted white vinegar or mild soapy warm water"
      ],
      steps: [
        "NEVER dry sweep with traditional brooms or feather dusters during severe smog days: sweeping flings settled ultra-fine toxic particles back into suspension where they float for 4 to 8 hours.",
        "If vacuuming, only use a vacuum with a certified sealed HEPA exhaust filter. Standard bagless vacuums blow sub-micron particles straight through their exhaust vents.",
        "Always use a slightly damp microfiber mop in an 'S' pattern across hard floors.",
        "Wipe horizontal surfaces (desks, window sills, headboards) with damp cloth folded into 8 sections, flipping to a clean fold per surface."
      ],
      proTips: "Add a drop of vegetable glycerin or mild dish soap to reduce static electricity on computer screens and furniture, keeping dust from clinging."
    },
    {
      id: "ventilation-window",
      title: "Strategic Thermal Inversion Ventilation Purge",
      difficulty: "Easy",
      cost: "₹0",
      cadRate: "Flush CO2 without saturating home with smog",
      effectiveness: "Keeps indoor CO2 below 850 ppm while keeping indoor PM2.5 controlled.",
      materials: [
        "Clock / Timer (15-20 min limit)",
        "Air purifier on High / Turbo mode ready"
      ],
      steps: [
        "During severe winter smog, NEVER ventilate at 6:00 AM - 10:00 AM or 7:00 PM - 11:00 PM (peak inversion and boundary layer compression).",
        "Check your local solar zenith: Between 12:30 PM and 2:30 PM, sunlight breaks the ground inversion, wind speeds pick up, and pollution concentrations reach diurnal lows.",
        "Perform a high-speed 'Cross-Ventilation Purge': Open opposite windows wide for exactly 15 to 20 minutes to rapidly replace stale CO2.",
        "Immediately seal all windows and blast your air purifier / Corsi-Rosenthal box on Turbo for 30 minutes to scrub any newly introduced outdoor particulates."
      ],
      proTips: "High indoor CO2 (>1200 ppm) causes brain fog, fatigue, and headaches. The timed 20-minute midday purge refreshes oxygen with minimal smog infiltration."
    }
  ],

  communityActions: [
    {
      id: "carpool-school",
      name: "Neighborhood School-Run Carpool Pods",
      category: "Transportation",
      impact: "Takes 12-16 idling cold-start cars off local school gates every morning; cuts local gate PM2.5 spikes by 48%.",
      description: "Organize 4 families into a rotating EV or low-emission carpool rota for neighborhood school trips instead of 4 individual idling vehicles.",
      badge: "Neighborhood Hero",
      participants: 42
    },
    {
      id: "smoke-watch",
      name: "Community Open-Burning & Smoke Spotter",
      category: "Enforcement & Civic",
      impact: "Alerts municipal emergency flying squads to illegal municipal trash burning and biomass smoke within 15 minutes.",
      description: "Geo-tag and photograph smoke plumes or illegal leaf/garbage fires and auto-generate an official report to local pollution control boards.",
      badge: "Clean Air Guardian",
      participants: 128
    },
    {
      id: "safe-havens",
      name: "Clean Air Safe Havens Directory",
      category: "Community Welfare",
      impact: "Provides clean breathing air (<25 µg/m³ PM2.5) for low-income families, students, and unhoused community members.",
      description: "Network of public libraries, community centers, and partner cafes with commercial grade HEPA systems open to the public during severe smog spikes.",
      badge: "Shelter from Smog",
      participants: 19
    },
    {
      id: "no-idling-zone",
      name: "Zero-Idle School Gates & Drive-Thrus",
      category: "Emissions Reduction",
      impact: "Eliminates toxic benzene, soot, and carbon monoxide accumulation right at children's breathing height.",
      description: "Community pledge and visual signage campaign requesting parents and delivery vans to turn off engines immediately while waiting.",
      badge: "Zero-Idle Leader",
      participants: 84
    },
    {
      id: "boiler-dialdown",
      name: "District Heating & Boiler Optimization",
      category: "Energy & Smog",
      impact: "Reduces neighborhood natural gas / coal / biomass demand by 7% per 1°C reduction, cutting regional NOx output.",
      description: "Coordinated community dial-down of home thermostats to 19°C (66°F) paired with thermal sweaters and electric throw blankets.",
      badge: "Thermal Conserver",
      participants: 61
    }
  ]
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = AERO_DATA;
}
