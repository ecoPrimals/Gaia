// pi-orient.js — π ports of contact on Earth
//
// Physical landmarks as orientation pores on the planet.
// The stone IS the Earth. The lichen grows on contact with it.
//
// Each landmark is a port — a pore on the planet's surface.
// The great circle between any two landmarks is a photon line.
// Light travel time across that line = physical time constant.
// Angular distance / π = how much of half-Earth you've crossed.
//
// π connects geometry to time:
//   half-circumference = π × radius
//   angular distance (radians) = arc / radius
//   photon time = arc / c
//
// Whatever you're studying — irrigation, investigation, data —
// sits at the CENTER. The landmarks orient around it.
//
// Kevin Mok / Tamison / ecoPrimal / attsi — ORCID 0009-0004-2141-0321

(function() {
  "use strict";

  var R = 6371.0;                   // Earth mean radius (km)
  var C = 299792.458;               // speed of light (km/s)
  var HALF_CIRC = Math.PI * R;      // half-circumference: π × R = 20,015 km
  var FULL_CIRC = 2 * Math.PI * R;  // full circumference: 2πR = 40,030 km
  var LIGHT_HALF = HALF_CIRC / C;   // photon time for half-Earth: ~66.8 ms

  // ═══════════════════════════════════════════════════════════════
  // LANDMARKS — π ports of contact
  //
  // Each has been used by humans for orientation across millennia.
  // Coordinates are WGS84 (lat/lon in degrees).
  // ═══════════════════════════════════════════════════════════════

  var LANDMARKS = {
    // ── STONE: ancient observatories ──
    "stonehenge": {
      name: "Stonehenge",
      lat: 51.1789, lon: -1.8262,
      kind: "stone", era: -3000,
      note: "Solstice alignment. 5000 years of continuous astronomical observation. Sarsen stones oriented to midsummer sunrise and midwinter sunset."
    },
    "easter_island": {
      name: "Rapa Nui (Easter Island)",
      lat: -27.1127, lon: -109.3497,
      kind: "stone", era: -400,
      note: "Most remote inhabited place on Earth. Moai face INWARD, watching the island. 887 statues. The lichen of human presence on volcanic stone."
    },
    "uluru": {
      name: "Uluru (Ayers Rock)",
      lat: -25.3444, lon: 131.0369,
      kind: "stone", era: -65000,
      note: "Oldest continuous civilization. Anangu Dreaming tracks. 600 million years of sandstone. The stone IS the story."
    },
    "giza": {
      name: "Great Pyramid of Giza",
      lat: 29.9792, lon: 31.1342,
      kind: "stone", era: -2560,
      note: "Oriented to true north within 3/60th of a degree. Base perimeter / height = 2π to 0.05% accuracy. π in stone."
    },
    "chichen_itza": {
      name: "Chichén Itzá (El Castillo)",
      lat: 20.6843, lon: -88.5678,
      kind: "stone", era: -600,
      note: "91 steps × 4 sides + platform = 365. Equinox serpent shadow. Time carved in limestone."
    },

    // ── WATER: orientation by flow ──
    "detroit": {
      name: "Detroit (the center)",
      lat: 42.3314, lon: -83.0458,
      kind: "water", era: 1701,
      note: "Le Détroit — the strait. Water connects Lake Huron to Lake Erie. The investigation sits here. The watering hole."
    },
    "confluence": {
      name: "Cahokia (Mississippi confluence)",
      lat: 38.6551, lon: -90.0615,
      kind: "water", era: -700,
      note: "Largest pre-Columbian city north of Mexico. Where Missouri meets Mississippi. Monks Mound: largest earthwork in the Americas."
    },
    "ganges_source": {
      name: "Gaumukh (Ganges source)",
      lat: 30.9267, lon: 79.0833,
      kind: "water", era: -1500,
      note: "Cow's mouth. Gangotri glacier at 4,000m. Source of irrigation for 400 million people. Water is core."
    },

    // ── SKY: celestial orientation ──
    "polaris": {
      name: "Polaris (via North Pole)",
      lat: 90.0, lon: 0.0,
      kind: "sky", era: null,
      note: "The one star that doesn't move. Your angle to Polaris IS your latitude. Navigation constant. The barre the dancer holds."
    },
    "south_celestial": {
      name: "South Celestial Pole (via South Pole)",
      lat: -90.0, lon: 0.0,
      kind: "sky", era: null,
      note: "No bright pole star in the south. The Southern Cross points the way. Absence as navigation — the null that orients."
    },

    // ── SIGNAL: communication landmarks ──
    "greenwich": {
      name: "Greenwich (Prime Meridian)",
      lat: 51.4769, lon: 0.0,
      kind: "signal", era: 1884,
      note: "Zero longitude. Time starts here. GMT/UTC origin. The arbitrary line the whole world agreed to use."
    },
    "date_line": {
      name: "International Date Line",
      lat: 0.0, lon: 180.0,
      kind: "signal", era: 1884,
      note: "Where today becomes yesterday. π radians from Greenwich. The anti-meridian. Cross it and time jumps."
    }
  };

  // ═══════════════════════════════════════════════════════════════
  // GEOMETRY — great circles, photon lines, π-fractions
  // ═══════════════════════════════════════════════════════════════

  function toRad(deg) { return deg * Math.PI / 180; }
  function toDeg(rad) { return rad * 180 / Math.PI; }

  // Great circle angular distance (radians) via Vincenty formula
  // More numerically stable than Haversine for antipodal points
  function angularDistance(lat1, lon1, lat2, lon2) {
    var φ1 = toRad(lat1), φ2 = toRad(lat2);
    var Δλ = toRad(lon2 - lon1);
    var sinφ1 = Math.sin(φ1), cosφ1 = Math.cos(φ1);
    var sinφ2 = Math.sin(φ2), cosφ2 = Math.cos(φ2);
    var sinΔλ = Math.sin(Δλ), cosΔλ = Math.cos(Δλ);

    var num = Math.sqrt(
      Math.pow(cosφ2 * sinΔλ, 2) +
      Math.pow(cosφ1 * sinφ2 - sinφ1 * cosφ2 * cosΔλ, 2)
    );
    var den = sinφ1 * sinφ2 + cosφ1 * cosφ2 * cosΔλ;
    return Math.atan2(num, den);
  }

  // Photon line between two landmarks
  function photonLine(id1, id2) {
    var a = LANDMARKS[id1], b = LANDMARKS[id2];
    if (!a || !b) return null;

    var σ = angularDistance(a.lat, a.lon, b.lat, b.lon);
    var arc = σ * R;                  // km along great circle
    var lightTime = arc / C;          // seconds
    var piFraction = σ / Math.PI;     // fraction of half-Earth (0..1)

    return {
      from: id1, to: id2,
      fromName: a.name, toName: b.name,
      angular_rad: σ,
      angular_deg: toDeg(σ),
      arc_km: arc,
      light_s: lightTime,
      light_ms: lightTime * 1000,
      light_μs: lightTime * 1000000,
      pi_fraction: piFraction,         // σ/π — how much of half-Earth
      pi_multiple: σ / Math.PI,        // same thing, for clarity
      bearing: initialBearing(a.lat, a.lon, b.lat, b.lon)
    };
  }

  // Initial bearing (degrees, 0=N, 90=E)
  function initialBearing(lat1, lon1, lat2, lon2) {
    var φ1 = toRad(lat1), φ2 = toRad(lat2);
    var Δλ = toRad(lon2 - lon1);
    var y = Math.sin(Δλ) * Math.cos(φ2);
    var x = Math.cos(φ1) * Math.sin(φ2) - Math.sin(φ1) * Math.cos(φ2) * Math.cos(Δλ);
    return (toDeg(Math.atan2(y, x)) + 360) % 360;
  }

  // ═══════════════════════════════════════════════════════════════
  // ORIENTATION — landmarks as compass around a center point
  //
  // Given a center (e.g. detroit), compute bearing + distance
  // to every landmark. This orients you on the planet.
  // ═══════════════════════════════════════════════════════════════

  function orient(centerId) {
    centerId = centerId || "detroit";
    var center = LANDMARKS[centerId];
    if (!center) return null;

    var bearings = [];
    for (var id in LANDMARKS) {
      if (id === centerId) continue;
      var line = photonLine(centerId, id);
      bearings.push({
        id: id,
        name: line.toName,
        kind: LANDMARKS[id].kind,
        bearing_deg: line.bearing,
        arc_km: line.arc_km,
        light_ms: line.light_ms,
        pi_fraction: line.pi_fraction,
        era: LANDMARKS[id].era
      });
    }

    // Sort by bearing (compass order, N=0 → E → S → W)
    bearings.sort(function(a, b) { return a.bearing_deg - b.bearing_deg; });

    return {
      center: centerId,
      centerName: center.name,
      lat: center.lat, lon: center.lon,
      landmarks: bearings,
      // π summary
      halfEarth_km: HALF_CIRC,
      lightHalfEarth_ms: LIGHT_HALF * 1000,
      // the farthest landmark gives the widest angle
      maxArc: bearings.reduce(function(m, b) {
        return b.arc_km > m ? b.arc_km : m;
      }, 0),
      // total π-fraction covered (sum of all arcs / half-circ)
      coverage: bearings.reduce(function(s, b) {
        return s + b.pi_fraction;
      }, 0)
    };
  }

  // ═══════════════════════════════════════════════════════════════
  // TIME BRAID — photon lines give time constants
  //
  // The pi-bus runs at π² ≈ 9.87s, π³ ≈ 31s, π⁴ ≈ 97s.
  // The photon lines give physical time that braids with π:
  //
  //   Detroit → Stonehenge:   ~19.9 ms   (0.00201 × π² s)
  //   Detroit → Easter Island: ~29.1 ms
  //   Detroit → Uluru:        ~51.1 ms
  //   Detroit → Polaris:      ~17.6 ms   (straight up, to N Pole)
  //   Half-Earth:             ~66.8 ms   (π × R / c)
  //   Full-Earth:            ~133.6 ms   (2π × R / c)
  //
  // These are THE time constants of the planet. They don't change.
  // Light from Stonehenge to Detroit takes 19.9 ms. Always.
  // That's the stone. The lichen grows on it.
  // ═══════════════════════════════════════════════════════════════

  function timeBraid(centerId) {
    var o = orient(centerId);
    if (!o) return null;

    var pi2_s = Math.PI * Math.PI;        // 9.87s
    var pi2_ms = pi2_s * 1000;            // 9870ms

    return {
      center: o.centerName,
      photon_lines: o.landmarks.map(function(lm) {
        return {
          to: lm.name,
          light_ms: Math.round(lm.light_ms * 1000) / 1000,
          pi_fraction: Math.round(lm.pi_fraction * 10000) / 10000,
          // how many photon trips fit in one π² bus cycle
          trips_per_pi2: Math.round(pi2_ms / lm.light_ms),
          kind: lm.kind
        };
      }),
      constants: {
        half_earth_ms: Math.round(LIGHT_HALF * 1000 * 1000) / 1000,
        full_earth_ms: Math.round(LIGHT_HALF * 2 * 1000 * 1000) / 1000,
        pi2_bus_ms: Math.round(pi2_ms),
        pi3_bus_ms: Math.round(pi2_s * Math.PI * 1000),
        pi4_bus_ms: Math.round(pi2_s * Math.PI * Math.PI * 1000),
        // π² bus cycle / half-Earth photon = how many times light
        // crosses half the planet in one bus tick
        pi2_over_halfEarth: Math.round(pi2_ms / (LIGHT_HALF * 1000))
      }
    };
  }

  // ═══════════════════════════════════════════════════════════════
  // STAR ANGLE — angle to Polaris = your latitude
  //
  // From any landmark, the angle to Polaris above the horizon
  // IS that landmark's latitude. This is how navigation works.
  // It's also the π-fraction of the quarter-Earth (pole to equator).
  // ═══════════════════════════════════════════════════════════════

  function polarisAngle(id) {
    var lm = LANDMARKS[id];
    if (!lm) return null;
    return {
      landmark: lm.name,
      latitude: lm.lat,
      polaris_elevation: lm.lat, // degrees above horizon
      quarter_earth_fraction: Math.abs(lm.lat) / 90,
      pi_half_fraction: toRad(Math.abs(lm.lat)) / (Math.PI / 2),
      hemisphere: lm.lat >= 0 ? "north" : "south",
      note: lm.lat >= 0
        ? "Polaris sits " + lm.lat.toFixed(1) + "° above your horizon"
        : "Polaris is " + Math.abs(lm.lat).toFixed(1) + "° below your horizon (use Southern Cross)"
    };
  }

  // ═══════════════════════════════════════════════════════════════
  // EXPOSE
  // ═══════════════════════════════════════════════════════════════

  window.PiOrient = {
    landmarks: LANDMARKS,
    photonLine: photonLine,
    orient: orient,
    timeBraid: timeBraid,
    polarisAngle: polarisAngle,
    angularDistance: angularDistance,
    constants: {
      R: R,                          // Earth radius (km)
      C: C,                          // speed of light (km/s)
      halfCirc: HALF_CIRC,           // π × R (km)
      fullCirc: FULL_CIRC,           // 2π × R (km)
      lightHalf_s: LIGHT_HALF,       // photon time for half-Earth
      lightFull_s: LIGHT_HALF * 2    // photon time for full-Earth
    }
  };

  console.log("[pi-orient] " + Object.keys(LANDMARKS).length + " landmarks loaded" +
    " · half-Earth = " + Math.round(HALF_CIRC) + " km" +
    " · photon half = " + (LIGHT_HALF * 1000).toFixed(1) + " ms" +
    " · π² bus = " + Math.round(Math.PI * Math.PI * 1000) + " ms");
})();
