/* io-probe.js — the membrane probes what I/O is available
 *
 * Every device is just a channel: { direction, bandwidth, latency, active }
 *   display   = output  (visual)
 *   touch     = input   (tactile)
 *   mouse     = input   (pointer)
 *   keyboard  = input   (symbolic)
 *   speaker   = output  (audio)
 *   mic       = input   (audio) — a speaker from the other side
 *   camera    = input   (visual) — a display from the other side
 *   gyro      = input   (spatial)
 *   vibrate   = output  (tactile) — touch from the other side
 *   network   = bidirectional (data)
 *   storage   = bidirectional (persistence)
 *   battery   = input   (energy state)
 *   gps       = input   (position)
 *
 * The HUD reads this and adapts. No breakpoints. Just channels.
 */

(function() {
  'use strict';

  const IO = {
    channels: {},
    ts: Date.now(),
    probed: false,

    // === PROBE ===
    probe: function() {
      const ch = {};

      // ── DISPLAY (output/visual) ──
      ch.display = {
        direction: 'output',
        type: 'visual',
        active: true,
        width: window.innerWidth,
        height: window.innerHeight,
        dpr: window.devicePixelRatio || 1,
        orientation: screen.orientation ? screen.orientation.type : 
                     (window.innerWidth > window.innerHeight ? 'landscape' : 'portrait'),
        colorDepth: screen.colorDepth || 24,
        bandwidth: window.innerWidth * window.innerHeight * (window.devicePixelRatio || 1),
      };

      // ── TOUCH (input/tactile) ──
      const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      ch.touch = {
        direction: 'input',
        type: 'tactile',
        active: hasTouch,
        points: navigator.maxTouchPoints || 0,
        coarse: matchMedia('(pointer: coarse)').matches,
        bandwidth: hasTouch ? navigator.maxTouchPoints * 60 : 0, // touches × framerate
      };

      // ── MOUSE (input/pointer) ──
      const hasFinePointer = matchMedia('(pointer: fine)').matches;
      const hasHover = matchMedia('(hover: hover)').matches;
      ch.mouse = {
        direction: 'input',
        type: 'pointer',
        active: hasFinePointer,
        hover: hasHover,
        fine: hasFinePointer,
        bandwidth: hasFinePointer ? 1000 : 0, // ~1000 Hz polling
      };

      // ── KEYBOARD (input/symbolic) ──
      ch.keyboard = {
        direction: 'input',
        type: 'symbolic',
        active: !hasTouch || hasFinePointer, // likely has physical keyboard
        virtual: hasTouch && !hasFinePointer, // likely virtual keyboard
        bandwidth: 15, // ~15 wpm average
      };

      // ── SPEAKER (output/audio) ──
      ch.speaker = {
        direction: 'output',
        type: 'audio',
        active: typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined',
        bandwidth: 44100, // sample rate
      };

      // ── MICROPHONE (input/audio — speaker from the other side) ──
      ch.mic = {
        direction: 'input',
        type: 'audio',
        active: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
        mirror: 'speaker', // a speaker from the other side
        bandwidth: 44100,
        // don't probe permission until user asks
        permitted: null,
      };

      // ── CAMERA (input/visual — display from the other side) ──
      ch.camera = {
        direction: 'input',
        type: 'visual',
        active: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
        mirror: 'display', // a display from the other side
        bandwidth: 0,
        permitted: null,
      };

      // ── GYRO/ACCELEROMETER (input/spatial) ──
      ch.gyro = {
        direction: 'input',
        type: 'spatial',
        active: typeof DeviceOrientationEvent !== 'undefined',
        bandwidth: hasTouch ? 60 : 0, // usually only on mobile
      };

      // ── VIBRATE (output/tactile — touch from the other side) ──
      ch.vibrate = {
        direction: 'output',
        type: 'tactile',
        active: typeof navigator.vibrate === 'function',
        mirror: 'touch', // touch from the other side
        bandwidth: 1, // binary on/off
      };

      // ── NETWORK (bidirectional/data) ──
      const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      ch.network = {
        direction: 'bidirectional',
        type: 'data',
        active: navigator.onLine,
        effectiveType: conn ? conn.effectiveType : 'unknown',
        downlink: conn ? conn.downlink : null, // Mbps
        rtt: conn ? conn.rtt : null, // ms
        saveData: conn ? conn.saveData : false,
        bandwidth: conn ? conn.downlink * 1000000 : null,
      };

      // ── STORAGE (bidirectional/persistence) ──
      ch.storage = {
        direction: 'bidirectional',
        type: 'persistence',
        active: typeof localStorage !== 'undefined',
        quota: null, // probe async below
        bandwidth: 10000000, // ~10MB/s for localStorage
      };

      // ── BATTERY (input/energy) ──
      ch.battery = {
        direction: 'input',
        type: 'energy',
        active: typeof navigator.getBattery === 'function',
        level: null,
        charging: null,
      };

      // ── GPS (input/position) ──
      ch.gps = {
        direction: 'input',
        type: 'position',
        active: typeof navigator.geolocation !== 'undefined',
        permitted: null,
        bandwidth: 1, // 1 Hz update rate
      };

      this.channels = ch;
      this.ts = Date.now();
      this.probed = true;

      // Async probes
      this._probeAsync();

      return ch;
    },

    _probeAsync: async function() {
      // Battery
      if (navigator.getBattery) {
        try {
          const batt = await navigator.getBattery();
          this.channels.battery.level = batt.level;
          this.channels.battery.charging = batt.charging;
          this.channels.battery.active = true;
        } catch(e) {}
      }
      // Storage quota
      if (navigator.storage && navigator.storage.estimate) {
        try {
          const est = await navigator.storage.estimate();
          this.channels.storage.quota = est.quota;
          this.channels.storage.usage = est.usage;
        } catch(e) {}
      }
      // Dispatch event when async probes complete
      window.dispatchEvent(new CustomEvent('io-probed', { detail: this }));
    },

    // === CLASSIFY ===
    // What kind of surface is this?
    classify: function() {
      const ch = this.channels;
      if (!this.probed) this.probe();

      const surface = {
        // Input capabilities
        canTouch: ch.touch.active,
        canPoint: ch.mouse.active,
        canType: ch.keyboard.active && !ch.keyboard.virtual,
        canSpeak: ch.mic.active,
        canSee: ch.camera.active,
        canMove: ch.gyro.active,

        // Output capabilities
        canShow: ch.display.active,
        canSound: ch.speaker.active,
        canVibrate: ch.vibrate.active,

        // Display metrics
        viewport: ch.display.width * ch.display.height,
        dpr: ch.display.dpr,
        orientation: ch.display.orientation,

        // Network
        online: ch.network.active,
        fast: ch.network.effectiveType === '4g' || ch.network.downlink > 5,
        saveData: ch.network.saveData,

        // Energy
        lowPower: ch.battery.level !== null && ch.battery.level < 0.15 && !ch.battery.charging,
      };

      // The surface profile — not "mobile" or "desktop", just capabilities
      surface.profile = [];
      if (surface.canTouch && !surface.canPoint) surface.profile.push('touch-only');
      if (surface.canTouch && surface.canPoint) surface.profile.push('hybrid');
      if (!surface.canTouch && surface.canPoint) surface.profile.push('pointer-only');
      if (surface.viewport < 400000) surface.profile.push('small');
      else if (surface.viewport < 1200000) surface.profile.push('medium');
      else surface.profile.push('large');
      if (surface.canMove) surface.profile.push('spatial');
      if (surface.lowPower) surface.profile.push('conserve');
      if (surface.saveData) surface.profile.push('conserve');

      // Set body classes based on profile
      document.body.classList.remove('io-touch-only', 'io-hybrid', 'io-pointer-only',
        'io-small', 'io-medium', 'io-large', 'io-spatial', 'io-conserve');
      surface.profile.forEach(p => document.body.classList.add('io-' + p));

      // Set CSS custom properties for adaptive layout
      document.documentElement.style.setProperty('--io-width', ch.display.width + 'px');
      document.documentElement.style.setProperty('--io-height', ch.display.height + 'px');
      document.documentElement.style.setProperty('--io-dpr', ch.display.dpr);
      document.documentElement.style.setProperty('--io-touch-points', ch.touch.points);
      const minTap = surface.canTouch ? 44 : 24;
      document.documentElement.style.setProperty('--io-min-tap', minTap + 'px');

      this.surface = surface;
      return surface;
    },

    // === PORES ===
    // The collapsed view. 13 channels become ~7 pores.
    // Each pore has inward + outward permeability. No input/output.
    // A display is a visual pore with high outward permeability.
    // A camera is the same pore from the other side.
    // A single photon diffracts any frame with a localized bubble of permeability.
    pores: function() {
      if (!this.probed) this.probe();
      var ch = this.channels;
      var pores = {};

      // VISUAL: display (out) + camera (in)
      var vOut = ch.display.active ? ch.display.bandwidth : 0;
      var vIn = ch.camera.active ? ch.camera.bandwidth : 0;
      var vTotal = vOut + vIn;
      pores.visual = {
        medium: 'visual', chirality: 'left-right',
        outward: vTotal > 0 ? vOut / vTotal : 0,
        inward: vTotal > 0 ? vIn / vTotal : 0,
        bandwidth: vTotal, open: vTotal > 0,
      };

      // AUDIO: speaker (out) + mic (in)
      var aOut = ch.speaker.active ? ch.speaker.bandwidth : 0;
      var aIn = ch.mic.active ? ch.mic.bandwidth : 0;
      var aTotal = aOut + aIn;
      pores.audio = {
        medium: 'audio', chirality: 'near-far',
        outward: aTotal > 0 ? aOut / aTotal : 0,
        inward: aTotal > 0 ? aIn / aTotal : 0,
        bandwidth: aTotal, open: aTotal > 0,
      };

      // TACTILE: vibrate (out) + touch (in)
      var tOut = ch.vibrate.active ? ch.vibrate.bandwidth : 0;
      var tIn = ch.touch.active ? ch.touch.bandwidth : 0;
      var tTotal = tOut + tIn;
      pores.tactile = {
        medium: 'tactile', chirality: 'cause-effect',
        outward: tTotal > 0 ? tOut / tTotal : 0,
        inward: tTotal > 0 ? tIn / tTotal : 0,
        bandwidth: tTotal, open: tTotal > 0,
      };

      // POINTER: mouse (mostly inward)
      if (ch.mouse.active) {
        pores.pointer = {
          medium: 'pointer', chirality: 'identity',
          inward: 0.95, outward: 0.05,
          bandwidth: ch.mouse.bandwidth, open: true,
        };
      }

      // SYMBOLIC: keyboard
      if (ch.keyboard.active) {
        var isVirtual = ch.keyboard.virtual;
        pores.symbolic = {
          medium: 'symbolic', chirality: 'identity',
          inward: isVirtual ? 0.7 : 0.9,
          outward: isVirtual ? 0.3 : 0.1,
          bandwidth: ch.keyboard.bandwidth, open: true,
        };
      }

      // SPATIAL: gyro
      if (ch.gyro.active) {
        pores.spatial = {
          medium: 'spatial', chirality: 'identity',
          inward: 0.9, outward: 0.1,
          bandwidth: ch.gyro.bandwidth, open: true,
        };
      }

      // DATA: network (balanced — the ur-barre)
      if (ch.network.active) {
        pores.data = {
          medium: 'data', chirality: 'identity',
          inward: 0.5, outward: 0.5,
          bandwidth: ch.network.bandwidth, open: true,
        };
      }

      // PERSISTENCE: storage (balanced)
      if (ch.storage.active) {
        pores.persistence = {
          medium: 'persistence', chirality: 'identity',
          inward: 0.5, outward: 0.5,
          bandwidth: ch.storage.bandwidth, open: true,
        };
      }

      return pores;
    },

    // === CHIRALITY ===
    // Mirror pairs have handedness. Left brain sees right.
    // The ballet dancer's left hand appears on the right in the mirror.
    chirality: {
      // camera↔display: selfie mirror — left becomes right
      'camera': { mirror: 'display', type: 'left-right', defaultAngle: 'toward' },
      // mic↔speaker: sound from here returns from there
      'mic':    { mirror: 'speaker', type: 'near-far',   defaultAngle: 'toward' },
      // touch↔vibrate: you press, it responds — same point, cause↔effect
      'touch':  { mirror: 'vibrate', type: 'cause-effect', defaultAngle: 'through' },
    },

    // Current reflection angle per mirror pair
    _angles: {},

    // === BARRE ===
    // The fixed reference the dancer holds. Channels that don't flip.
    // Network, storage, keyboard, gyro — structural, no chirality.
    barre: function() {
      if (!this.probed) this.probe();
      var mirrorNames = {};
      Object.keys(this.chirality).forEach(function(k) {
        mirrorNames[k] = true;
        mirrorNames[IO.chirality[k].mirror] = true;
      });
      return Object.entries(this.channels)
        .filter(function(e) { return e[1].active && !mirrorNames[e[0]]; })
        .map(function(e) { return e[0]; });
    },

    // === ROTATE ===
    // Dancer turns. Same mirror, different view.
    // 'toward' = selfie/ballet (left↔right active)
    // 'away'   = rear camera (chirality cancels for visual)
    // 'through' = AR overlay (transparent, no flip)
    rotate: function(channelName, angle) {
      this._angles[channelName] = angle;
    },

    // === REFLECTION ===
    // What the dancer actually sees from each mirror at current angle.
    reflection: function() {
      var self = this;
      return Object.entries(this.chirality).map(function(e) {
        var name = e[0], spec = e[1];
        var angle = self._angles[name] || spec.defaultAngle;
        var baseChirality = spec.type;
        var effective;
        if (angle === 'through') {
          effective = 'identity';
        } else if (angle === 'away' && baseChirality === 'left-right') {
          effective = 'identity';
        } else {
          effective = baseChirality;
        }
        return {
          input: name,
          output: spec.mirror,
          angle: angle,
          baseChirality: baseChirality,
          effectiveChirality: effective,
        };
      });
    },

    // === SUMMARY ===
    summary: function() {
      if (!this.probed) this.probe();
      const active = Object.entries(this.channels)
        .filter(([_, ch]) => ch.active)
        .map(([name, ch]) => name + ' (' + ch.direction + '/' + ch.type + ')');
      const mirrors = Object.entries(this.channels)
        .filter(([_, ch]) => ch.mirror)
        .map(([name, ch]) => name + ' ↔ ' + ch.mirror);
      return {
        active: active,
        mirrors: mirrors,
        profile: this.surface ? this.surface.profile : [],
        channels: Object.keys(this.channels).length,
        openChannels: active.length,
        barre: this.barre(),
        reflection: this.reflection(),
      };
    },
  };

  // Auto-probe on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { IO.probe(); IO.classify(); });
  } else {
    IO.probe();
    IO.classify();
  }

  // Re-probe on resize/orientation change
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => { IO.probe(); IO.classify(); }, 250);
  });
  if (screen.orientation) {
    screen.orientation.addEventListener('change', () => { IO.probe(); IO.classify(); });
  }

  // Expose globally
  window.IO = IO;

})();
