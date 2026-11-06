/**
 * Stadial — Deep time orientation for the membrane.
 *
 * The Earth breathes on geological time. Stadials (cold, ice advance)
 * and interstadials (warm, bloom) are inhale/exhale at planetary scale.
 *
 * Pattern: tectonic sets the stage → ice carves → water fills → life blooms.
 * Same as: infrastructure → defense → data → ecosystem.
 *
 * Case study: Grand Tetons.
 *   13 Ma fault → 150 ka Bull Lake ice → 30-12 ka Pinedale sculpt →
 *   12 ka deglaciation fills Jenny Lake → now: bloom on 13M years of work.
 *
 * Kevin Mok / Tamison / ecoPrimal / attsi
 * ORCID 0009-0004-2141-0321
 */

(function () {
  "use strict";

  /* ── Climate phases ── */
  const STADIAL      = "stadial";       // cold, ice advance, contraction
  const INTERSTADIAL = "interstadial";  // warm, bloom, expansion
  const TRANSITION   = "transition";    // between states

  /* ── Shaping forces ── */
  const TECTONIC   = "tectonic";    // faulting, uplift — sets the stage
  const GLACIAL    = "glacial";     // ice carving — sculpts
  const FLUVIAL    = "fluvial";     // water erosion/fill — fills
  const AEOLIAN    = "aeolian";     // wind — scatters
  const BIOLOGICAL = "biological";  // soil, vegetation — blooms

  /* ── Geological periods ── */
  const PERIODS = [
    // Deep time — tectonic stage-setting
    { id: "laramide",         name: "Laramide Orogeny",            start: 80e6,  end: 35e6,  phase: INTERSTADIAL, force: TECTONIC,   temp:  4.0, sea:  100, note: "Rocky Mountain uplift. Ancestral Tetons begin." },
    { id: "miocene_warm",     name: "Miocene Climatic Optimum",    start: 17e6,  end: 13e6,  phase: INTERSTADIAL, force: BIOLOGICAL, temp:  4.0, sea:   40, note: "Warmest since Eocene. Grasslands spread." },
    { id: "teton_fault",      name: "Teton Fault Initiation",      start: 13e6,  end: 2.6e6, phase: INTERSTADIAL, force: TECTONIC,   temp:  2.0, sea:   25, note: "Normal fault. West block rises (Tetons), east drops (Jackson Hole). No foothills." },

    // Pleistocene — the sculptor
    { id: "pleistocene_onset",name: "Pleistocene Onset",           start: 2.6e6, end: 2e6,   phase: TRANSITION,   force: GLACIAL,    temp: -4.0, sea:  -60, note: "First major Northern Hemisphere glaciation." },
    { id: "pre_illinoian",    name: "Pre-Illinoian Glacials",      start: 2e6,   end: 300e3, phase: STADIAL,      force: GLACIAL,    temp: -6.0, sea: -100, note: "Multiple glacial advances. Early Teton canyon carving." },
    { id: "bull_lake",        name: "Bull Lake Glaciation",        start: 200e3, end: 130e3, phase: STADIAL,      force: GLACIAL,    temp: -6.0, sea: -120, note: "Carved initial U-valleys: Cascade, Death, Paintbrush canyons. Ice >1km thick." },
    { id: "sangamon",         name: "Sangamonian Interglacial",    start: 130e3, end: 75e3,  phase: INTERSTADIAL, force: FLUVIAL,    temp:  1.0, sea:    6, note: "Warmer than today. Teton valleys fill with sediment. Rivers re-establish." },
    { id: "early_wisconsin",  name: "Early Wisconsin Glacial",     start: 75e3,  end: 30e3,  phase: STADIAL,      force: GLACIAL,    temp: -5.0, sea:  -80, note: "Ice rebuilds. Cascade Canyon reoccupied." },
    { id: "pinedale",         name: "Pinedale Glaciation",         start: 30e3,  end: 12e3,  phase: STADIAL,      force: GLACIAL,    temp: -8.0, sea: -130, note: "Maximum ice. The Tetons as we know them. 12 glaciers. LGM at 21ka: ice 2km thick." },
    { id: "younger_dryas",    name: "Younger Dryas",               start: 12900, end: 11700, phase: STADIAL,      force: GLACIAL,    temp: -6.0, sea:  -60, note: "1300 years of sudden cold. Teton glaciers briefly readvance." },
    { id: "holocene_thermal", name: "Holocene Climatic Optimum",   start: 9000,  end: 5000,  phase: INTERSTADIAL, force: BIOLOGICAL, temp:  1.0, sea:    0, note: "Warmest Holocene. Jenny Lake, Leigh Lake reach current form." },
    { id: "neoglacial",       name: "Neoglaciation",               start: 5000,  end: 150,   phase: STADIAL,      force: GLACIAL,    temp: -0.5, sea:   -1, note: "Cool periods. Little Ice Age. Teton Glacier maximum ~1850." },
    { id: "anthropocene",     name: "Anthropocene",                start: 150,   end: 0,     phase: TRANSITION,   force: BIOLOGICAL, temp:  1.1, sea:  0.2, note: "Teton Glacier retreating 3m/yr. What ice built in 150ka changes in 150yr." },
  ];

  /* ── Grand Teton formation events ── */
  const TETON_EVENTS = [
    { period: "laramide",         force: TECTONIC,   action: "Compressional orogeny lifts Precambrian basement rock", result: "2.7Ga gneiss and granite exposed. Ancestral Rocky Mountain block." },
    { period: "teton_fault",      force: TECTONIC,   action: "Normal fault drops east block 6km. West block rises. No foothills.", result: "64km long, 21km wide. Grand Teton 4199m. Jackson Hole 1900m. 2300m relief." },
    { period: "bull_lake",        force: GLACIAL,    action: "Valley glaciers fill Cascade, Death, Paintbrush canyons. Ice >1km.", result: "Initial U-shaped valleys. Peaks become nunataks above the ice." },
    { period: "pinedale",         force: GLACIAL,    action: "12 glaciers carve simultaneously. Cirques deepen. Arêtes sharpen.", result: "Cathedral Group: Grand Teton, Mt Owen, Teewinot. Moraines dam future lakes." },
    { period: "pinedale",         force: GLACIAL,    action: "Glacial plucking on north/east faces. Freeze-thaw shatters ridgelines.", result: "North face: 600m vertical granite. Cathedral Traverse. Exum Ridge." },
    { period: "sangamon",         force: FLUVIAL,    action: "Meltwater fills moraine-dammed basins. Rivers cut through outwash.", result: "Proto-Jenny Lake. Snake River establishes course." },
    { period: "holocene_thermal", force: FLUVIAL,    action: "Final deglaciation fills lakes. Streams cascade from hanging valleys.", result: "Jenny Lake (480ha, 73m deep), Leigh, Bradley, Taggart, Phelps. 7 moraine-dammed lakes." },
    { period: "holocene_thermal", force: BIOLOGICAL, action: "Forests climb to 3000m. Meadows fill valley floors.", result: "The ecosystem: grizzly, elk, moose, pika, trumpeter swan." },
    { period: "anthropocene",     force: BIOLOGICAL, action: "Teton Glacier retreating 3m/yr. Whitebark pine dying.", result: "The bloom shifts. 150ka of work changes in 150yr." },
  ];

  /* ── Grand Teton + Jackson Hole landmarks ── */
  const TETON_LANDMARKS = [
    { id: "grand_tetons",  name: "Grand Teton",   lat: 43.7413, lon: -110.8024, kind: "stone", era: -13000000, note: "No foothills. 2.7Ga gneiss. 2300m above Jackson Hole. Ice carved, water filled." },
    { id: "jackson_hole",  name: "Jackson Hole",   lat: 43.4799, lon: -110.7624, kind: "water", era: -13000000, note: "The down-thrown block. What drops makes the valley. Snake River runs through." },
    { id: "jenny_lake",    name: "Jenny Lake",     lat: 43.7530, lon: -110.7270, kind: "water", era: -12000,    note: "Pinedale moraine-dammed. 480ha, 73m deep. The water that fills what ice carved." },
    { id: "teton_glacier",name: "Teton Glacier",   lat: 43.7450, lon: -110.8080, kind: "stone", era: -5000,     note: "Neoglacial remnant. Retreating 3m/yr. May disappear by 2030." },
  ];

  /* ── Queries ── */

  /** All geological periods, oldest first. */
  function periods() { return [...PERIODS].sort((a, b) => b.start - a.start); }

  /** Stadial periods only. */
  function stadials() { return PERIODS.filter(p => p.phase === STADIAL); }

  /** Interstadial periods only. */
  function interstadials() { return PERIODS.filter(p => p.phase === INTERSTADIAL); }

  /** The climate rhythm — phase + duration pairs, oldest first. */
  function rhythm() {
    return periods().map(p => ({
      phase: p.phase,
      duration_ya: p.start - p.end,
      name: p.name,
      temp: p.temp,
    }));
  }

  /** Find which period we're in now (or at a given years-ago). */
  function periodAt(ya) {
    if (ya === undefined) ya = 0;
    return PERIODS.find(p => ya >= p.end && ya < p.start) || null;
  }

  /** Grand Teton formation trace — events with their periods, oldest first. */
  function tetonTrace() {
    return TETON_EVENTS.map(e => {
      const period = PERIODS.find(p => p.id === e.period);
      return { ...e, period_name: period ? period.name : e.period, start: period ? period.start : 0, phase: period ? period.phase : "unknown" };
    }).sort((a, b) => b.start - a.start);
  }

  /** Formation pattern — the sequence of forces that built the Tetons. */
  function formationPattern() {
    const trace = tetonTrace();
    const forces = [...new Set(trace.map(e => e.force))];
    return {
      forces,
      pattern: "tectonic → glacial → fluvial → biological",
      analogy: "infrastructure → defense → data → ecosystem",
      events: trace.length,
    };
  }

  /** Teton landmarks (extension of PiOrient landmarks). */
  function tetonLandmarks() { return [...TETON_LANDMARKS]; }

  /**
   * Time scale — express a duration in human-readable geological scale.
   * Returns { value, unit, scale }.
   */
  function timeScale(ya) {
    if (ya >= 1e9) return { value: ya / 1e9,  unit: "Ga", scale: "billion years" };
    if (ya >= 1e6) return { value: ya / 1e6,  unit: "Ma", scale: "million years" };
    if (ya >= 1e3) return { value: ya / 1e3,  unit: "ka", scale: "thousand years" };
    return { value: ya, unit: "ya", scale: "years ago" };
  }

  /**
   * Temperature curve — returns periods as {ya, temp} points for graphing.
   * Points at midpoint of each period.
   */
  function tempCurve() {
    return periods().map(p => ({
      ya: (p.start + p.end) / 2,
      temp: p.temp,
      name: p.name,
      phase: p.phase,
    }));
  }

  /**
   * Sea level curve — same structure as tempCurve but for sea level.
   */
  function seaCurve() {
    return periods().map(p => ({
      ya: (p.start + p.end) / 2,
      sea: p.sea,
      name: p.name,
      phase: p.phase,
    }));
  }

  /** Phase summary — counts and total duration by phase. */
  function phaseSummary() {
    const summary = {};
    for (const p of PERIODS) {
      if (!summary[p.phase]) summary[p.phase] = { count: 0, total_ya: 0, periods: [] };
      summary[p.phase].count++;
      summary[p.phase].total_ya += p.start - p.end;
      summary[p.phase].periods.push(p.name);
    }
    return summary;
  }

  /**
   * The analogy map — how geological forces map to membrane forces.
   */
  function analogyMap() {
    return [
      { geo: TECTONIC,   membrane: "infrastructure", cns: "autonomic",  note: "Sets the stage. Faulting = provisioning. Uplift = deployment." },
      { geo: GLACIAL,    membrane: "immune",          cns: "immune",     note: "Sculpts by removal. Ice carves channels = defense carves pores." },
      { geo: FLUVIAL,    membrane: "data",            cns: "sensory",    note: "Fills what was carved. Water fills lakes = data fills channels." },
      { geo: AEOLIAN,    membrane: "scatter",          cns: "immune",     note: "Scatters. Wind deposits = scatter maze distributes." },
      { geo: BIOLOGICAL, membrane: "ecosystem",        cns: "cortex",     note: "Blooms on what's built. Life colonizes = ecosystem grows." },
    ];
  }

  /* ── Set body attributes ── */
  function stamp() {
    const now = periodAt(0);
    if (now) {
      document.body.setAttribute("data-stadial-period", now.id);
      document.body.setAttribute("data-stadial-phase", now.phase);
      document.body.setAttribute("data-stadial-temp", now.temp);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", stamp);
  } else {
    stamp();
  }

  /* ── Expose ── */
  window.Stadial = {
    PERIODS,
    TETON_EVENTS,
    TETON_LANDMARKS,
    periods,
    stadials,
    interstadials,
    rhythm,
    periodAt,
    tetonTrace,
    formationPattern,
    tetonLandmarks,
    timeScale,
    tempCurve,
    seaCurve,
    phaseSummary,
    analogyMap,
  };

})();
