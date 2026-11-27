/* sky.js - the sun, the moon and the fixed stars from the clock alone. One file, read by the atlas and by the HUD, so both show the
   same sky. Nothing is fetched: every number is worked out here from the moment asked.

   gaiaSky(ms)                 the place on earth the sun stands straight over, the same for the moon, how far the moon
                               is (earth radii), how far round from the sun it has gone (elong, degrees) and how much of
                               its face is lit (0..1). ms is the ordinary clock: milliseconds of UT since 1970.
   gaiaSky.look(place, ms)     the sky from a place {lat, lon}: how high the sun and the moon stand, which way they lie,
                               and how the lit edge of the moon is turned as seen from there.
   gaiaSky.next(place, ms, 'sun'|'moon', 'rise'|'set')   the next rising or setting seen from a place.
   gaiaSky.moonFace(ctx, x, y, r, lit, tilt)             draws the moon as it is seen.
   gaiaSky.stars(catalogue, ms)  the place on earth every star of /static/atlas-stars.json stands straight over at that
                               time. That file is the one thing read from outside this one, and the page hands it in.
   gaiaSky.dome(ctx, size, place, ms, catalogue)         draws the whole sky from a place as a round chart: overhead in
                               the middle, the horizon the rim, north at the top, east on the left.
   gaiaSky.round(ctx, w, h, place, ms, catalogue)        draws the same sky as a strip all the way round the horizon:
                               north at both ends, east, south in the middle, west; the foot is the horizon.
   gaiaSky.stamp(ms) / .read(text) / .of(y, m, d, h, min)   dates. Before 15 October 1582 they are in the old (Julian)
                               calendar, the one the annals count in; from that day on, the calendar in use now.
   gaiaSky.easter(year)        Easter Sunday by the Alexandrian table (the old calendar's until 1582, today's after).

   HOW GOOD. The method is Paul Schlyter's (stjarnhimlen.se), with three things added so that it holds over
   centuries: the slow second-order drift of the sun's and the moon's mean motions (Meeus, Astronomical Algorithms),
   Greenwich sidereal time by Meeus's formula, and the slowing of the earth's turning (delta-T, Espenak and Meeus's
   fit to Morrison and Stephenson). Held against an independent ephemeris (PyEphem) at 500 moments from 700 BC to
   now: the place under the sun agrees to 0.03 of a degree, the place under the moon to a tenth of a degree, and the
   lit share of the moon to 0.002. It also puts the three eclipses of the moon Ptolemy records from Alexandria
   (AD 133, 134, 136) and the eclipse of the sun in the Irish annals (1 May 664) on their nights.
   That agreement does not cover how much the earth's turning has slowed: both reckonings take it from much the same
   fit, and long ago it is known only to a few minutes - a degree or so of longitude for where a body stood overhead,
   a few minutes for a rising or a setting. Phases and dates do not depend on it.

   THE STARS are moved from where the catalogue has them in the year 2000 by their own drift and by the slow turning
   of the earth's axis. Held against PyEphem for 122 stars at 160 moments from 2999 BC to now, the places agree to
   0.02 of a degree. PyEphem turns the axis by the same formula, so that agreement checks the arithmetic and not
   the formula, which is fitted to the present and is trusted less the further back it is taken. Two things written
   down by others stand with it: the pole star comes nearest the pole in 2102, 0.46 of a degree off (the almanacs
   say about 2100, 0.45), and Regulus and Spica stand here, for AD 137, 1.5 and 1.3 degrees further along the sun's
   path than Ptolemy's own catalogue has them - about the error that catalogue is known for, a degree and more. */
(function (root) {
  'use strict';
  var DEG = Math.PI / 180, DAY = 86400000;
  var REFORM = Date.UTC(1582, 9, 15);                                // the first day of the calendar in use now
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function rev(x) { return x - Math.floor(x / 360) * 360; }
  function kepler(M, e) { var E = M + e * Math.sin(M) * (1 + e * Math.cos(M)), k = 0, dE; do { dE = (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E)); E -= dE; } while (Math.abs(dE) > 1e-9 && ++k < 30); return E; }

  // how far the even clock of the heavens runs ahead of the earth's own turning, in seconds, for a year (with its fraction)
  function deltaT(y) {
    var u, t;
    if (y < -500) { u = (y - 1820) / 100; return -20 + 32 * u * u; }
    if (y < 500) { u = y / 100; return 10583.6 - 1014.41 * u + 33.78311 * u * u - 5.952053 * Math.pow(u, 3) - 0.1798452 * Math.pow(u, 4) + 0.022174192 * Math.pow(u, 5) + 0.0090316521 * Math.pow(u, 6); }
    if (y < 1600) { u = (y - 1000) / 100; return 1574.2 - 556.01 * u + 71.23472 * u * u + 0.319781 * Math.pow(u, 3) - 0.8503463 * Math.pow(u, 4) - 0.005050998 * Math.pow(u, 5) + 0.0083572073 * Math.pow(u, 6); }
    if (y < 1700) { t = y - 1600; return 120 - 0.9808 * t - 0.01532 * t * t + Math.pow(t, 3) / 7129; }
    if (y < 1800) { t = y - 1700; return 8.83 + 0.1603 * t - 0.0059285 * t * t + 0.00013336 * Math.pow(t, 3) - Math.pow(t, 4) / 1174000; }
    if (y < 1860) { t = y - 1800; return 13.72 - 0.332447 * t + 0.0068612 * t * t + 0.0041116 * Math.pow(t, 3) - 0.00037436 * Math.pow(t, 4) + 0.0000121272 * Math.pow(t, 5) - 0.0000001699 * Math.pow(t, 6) + 0.000000000875 * Math.pow(t, 7); }
    if (y < 1900) { t = y - 1860; return 7.62 + 0.5737 * t - 0.251754 * t * t + 0.01680668 * Math.pow(t, 3) - 0.0004473624 * Math.pow(t, 4) + Math.pow(t, 5) / 233174; }
    if (y < 1920) { t = y - 1900; return -2.79 + 1.494119 * t - 0.0598939 * t * t + 0.0061966 * Math.pow(t, 3) - 0.000197 * Math.pow(t, 4); }
    if (y < 1941) { t = y - 1920; return 21.20 + 0.84493 * t - 0.076100 * t * t + 0.0020936 * Math.pow(t, 3); }
    if (y < 1961) { t = y - 1950; return 29.07 + 0.407 * t - t * t / 233 + Math.pow(t, 3) / 2547; }
    if (y < 1986) { t = y - 1975; return 45.45 + 1.067 * t - t * t / 260 - Math.pow(t, 3) / 718; }
    if (y < 2005) { t = y - 2000; return 63.86 + 0.3345 * t - 0.060374 * t * t + 0.0017275 * Math.pow(t, 3) + 0.000651814 * Math.pow(t, 4) + 0.00002373599 * Math.pow(t, 5); }
    if (y < 2050) { t = y - 2000; return 62.92 + 0.32217 * t + 0.005589 * t * t; }
    if (y < 2150) { u = (y - 1820) / 100; return -20 + 32 * u * u - 0.5628 * (2150 - y); }
    u = (y - 1820) / 100; return -20 + 32 * u * u;
  }

  function turn(ms) {                                                 // how far the earth has turned against the stars (Greenwich sidereal time, degrees), from the ordinary clock
    var du = ms / DAY - 10957.5, Tu = du / 36525;
    return rev(280.46061837 + 360.98564736629 * du + 0.000387933 * Tu * Tu - Tu * Tu * Tu / 38710000);
  }

  function sky(ms) {
    var dt = deltaT(2000 + (ms - 946684800000) / (365.2425 * DAY));
    var d = (ms + dt * 1000) / DAY - 10956;                           // days from 1999 Dec 31, 0h, on the even clock
    var T = (d - 1.5) / 36525, T2 = T * T;                            // centuries from the year 2000
    var ws = 282.9404 + 4.70935e-5 * d + 0.0004569 * T2, es = 0.016709 - 1.151e-9 * d, Ms = rev(356.0470 + 0.9856002585 * d - 0.0001537 * T2), ecl = (23.4393 - 3.563e-7 * d) * DEG;
    var E = kepler(Ms * DEG, es), lonS = Math.atan2(Math.sqrt(1 - es * es) * Math.sin(E), Math.cos(E) - es) + ws * DEG;
    var Ls = rev(Ms + ws);
    var gmst = turn(ms);
    function over(lon, lat) {                                         // ecliptic place in the sky -> the place on earth it stands straight over
      var x = Math.cos(lat) * Math.cos(lon), y = Math.cos(lat) * Math.sin(lon), z = Math.sin(lat);
      var ye = y * Math.cos(ecl) - z * Math.sin(ecl), ze = y * Math.sin(ecl) + z * Math.cos(ecl);
      return {lat: Math.asin(ze) / DEG, lon: rev(Math.atan2(ye, x) / DEG - gmst + 180) - 180};
    }
    var Nm = (125.1228 - 0.0529538083 * d + 0.0020754 * T2) * DEG, im = 5.1454 * DEG, wm = (318.0634 + 0.1643573223 * d - 0.0123954 * T2), Mm = rev(115.3654 + 13.0649929509 * d + 0.0087414 * T2), em = 0.0549;
    var Em = kepler(Mm * DEG, em), xv = 60.2666 * (Math.cos(Em) - em), yv = 60.2666 * Math.sqrt(1 - em * em) * Math.sin(Em);
    var r = Math.sqrt(xv * xv + yv * yv), u = Math.atan2(yv, xv) + wm * DEG;
    var xh = r * (Math.cos(Nm) * Math.cos(u) - Math.sin(Nm) * Math.sin(u) * Math.cos(im)),
        yh = r * (Math.sin(Nm) * Math.cos(u) + Math.cos(Nm) * Math.sin(u) * Math.cos(im)), zh = r * Math.sin(u) * Math.sin(im);
    var lonM = Math.atan2(yh, xh) / DEG, latM = Math.atan2(zh, Math.sqrt(xh * xh + yh * yh)) / DEG;
    var Lm = rev(Nm / DEG + wm + Mm), D = (Lm - Ls) * DEG, F = (Lm - Nm / DEG) * DEG, a = Mm * DEG, b = Ms * DEG;
    lonM += -1.274 * Math.sin(a - 2 * D) + 0.658 * Math.sin(2 * D) - 0.186 * Math.sin(b) - 0.059 * Math.sin(2 * a - 2 * D)
      - 0.057 * Math.sin(a - 2 * D + b) + 0.053 * Math.sin(a + 2 * D) + 0.046 * Math.sin(2 * D - b) + 0.041 * Math.sin(a - b)
      - 0.035 * Math.sin(D) - 0.031 * Math.sin(a + b) - 0.015 * Math.sin(2 * F - 2 * D) + 0.011 * Math.sin(a - 4 * D);
    latM += -0.173 * Math.sin(F - 2 * D) - 0.055 * Math.sin(a - F - 2 * D) - 0.046 * Math.sin(a + F - 2 * D) + 0.033 * Math.sin(F + 2 * D) + 0.017 * Math.sin(2 * a + F);
    r += -0.58 * Math.cos(a - 2 * D) - 0.46 * Math.cos(2 * D);
    var elong = rev(lonM - lonS / DEG);
    return {sun: over(lonS, 0), moon: over(lonM * DEG, latM * DEG), far: r, elong: elong, lit: (1 - Math.cos(elong * DEG)) / 2,
            moonLat: latM, deltaT: dt};
  }

  function apart(p, q) {                                              // degrees between two places, measured at the core
    var c = Math.sin(p.lat * DEG) * Math.sin(q.lat * DEG) + Math.cos(p.lat * DEG) * Math.cos(q.lat * DEG) * Math.cos((p.lon - q.lon) * DEG);
    return Math.acos(Math.max(-1, Math.min(1, c))) / DEG;
  }
  function bearing(p, q) {                                            // the way the shortest line from p to q sets out, round from north
    var a = p.lat * DEG, b = q.lat * DEG, d = (q.lon - p.lon) * DEG;
    return (Math.atan2(Math.sin(d) * Math.cos(b), Math.cos(a) * Math.sin(b) - Math.sin(a) * Math.cos(b) * Math.cos(d)) / DEG + 360) % 360;
  }
  // The sky from a place. A body stands as high as 90 degrees less its distance over the ground from the place it is
  // straight over, and lies the way the shortest line to that place sets out. The moon is near enough that standing on
  // the surface instead of at the core lowers it by up to a degree; that is taken off.
  function look(place, ms, s) {
    s = s || sky(ms);
    var sunUp = 90 - apart(place, s.sun), moonUp = 90 - apart(place, s.moon);
    moonUp -= Math.asin(Math.cos(moonUp * DEG) / s.far) / DEG;
    // the lit edge points at the sun. Seen from inside the sky a turn runs the other way round than on the ground.
    var tilt = ((bearing(s.moon, place) - bearing(s.moon, s.sun)) % 360 + 360) % 360;
    return {sun: {up: sunUp, way: bearing(place, s.sun)}, moon: {up: moonUp, way: bearing(place, s.moon), tilt: tilt},
            lit: s.lit, elong: s.elong, far: s.far};
  }
  var EDGE = {sun: -0.833, moon: 0.125};                              // the upper edge on the sea horizon, bent air counted
  function height(place, ms, body) { var l = look(place, ms); return l[body].up - EDGE[body]; }
  function next(place, ms, body, what) {                              // the next rising or setting after ms, or null if there is none within two days
    var step = 10 * 60000, rise = what !== 'set', a = height(place, ms, body), t, b, lo, hi, mid;
    for (t = ms + step; t <= ms + 2 * DAY; t += step) {
      b = height(place, t, body);
      if (rise ? (a < 0 && b >= 0) : (a >= 0 && b < 0)) {
        lo = t - step; hi = t;
        for (var i = 0; i < 22; i++) { mid = (lo + hi) / 2; if ((height(place, mid, body) >= 0) === rise) hi = mid; else lo = mid; }
        return hi;
      }
      a = b;
    }
    return null;
  }

  // the moon as it is seen: lit is the share of the face in light, tilt is where the lit edge points, in degrees
  // clockwise from straight up. Without a tilt the lit edge is drawn to the right.
  function moonFace(ctx, x, y, r, lit, tilt, dark, light) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(((tilt == null ? 90 : tilt) - 90) * DEG);
    ctx.beginPath(); ctx.arc(0, 0, r, 0, 2 * Math.PI); ctx.fillStyle = dark || '#161c24'; ctx.fill();
    ctx.beginPath(); ctx.arc(0, 0, r, -Math.PI / 2, Math.PI / 2);                      // the half toward the sun
    var w = r * Math.abs(1 - 2 * lit);
    if (lit >= 0.5) ctx.ellipse(0, 0, w, r, 0, Math.PI / 2, 1.5 * Math.PI);            // more than half: the light reaches past the middle
    else ctx.ellipse(0, 0, w, r, 0, Math.PI / 2, -Math.PI / 2, true);                  // less: the dark reaches into the lit half
    ctx.closePath(); ctx.fillStyle = light || '#dfe3e9'; ctx.fill();
    ctx.beginPath(); ctx.arc(0, 0, r, 0, 2 * Math.PI); ctx.strokeStyle = 'rgba(200,214,229,.55)'; ctx.lineWidth = 1; ctx.stroke();
    ctx.restore();
  }
  function moonName(e) { return ['new', 'waxing crescent', 'first quarter', 'waxing gibbous', 'full', 'waning gibbous', 'last quarter', 'waning crescent'][Math.floor(((e + 22.5) % 360) / 45)]; }

  // ---------------------------------------------------------------- the fixed stars
  // cat is /static/atlas-stars.json: six numbers a star, as that file says. Given a time this fills, for every star,
  // the place on earth it stands straight over (lat is its declination at that time; lon is its right ascension less
  // the turn of the earth), with its brightness and colour. Two things move a star between the year 2000 and the time
  // asked: its own drift, taken as steady, and the slow turning of the earth's axis (precession, by the angles of
  // Lieske 1976 as Meeus gives them), which carries the pole round the sky in some 26,000 years. The small nodding of
  // the axis and the bending of starlight by the earth's motion (a third of a minute of arc each) are left out.
  // The arrays are kept on the catalogue and filled again when another time is asked.
  function stars(cat, ms) {
    var n = cat.n, s = cat.s, k = cat._k, i, j;
    if (!k) {
      k = cat._k = {n: n, lat: new Float32Array(n), lon: new Float32Array(n), ra: new Float32Array(n), mag: new Float32Array(n), bv: new Float32Array(n), at: null};
      for (i = 0; i < n; i++) { k.mag[i] = s[i * 6 + 2] / 100; k.bv[i] = s[i * 6 + 3] / 100; }
    }
    if (k.at == null || Math.abs(ms - k.at) > 30 * DAY) {             // the axis turns 50 seconds of arc a year: a month is nothing
      var yrs = (ms - 946728000000) / (365.25 * DAY), T = yrs / 100, AS = DEG / 3600;
      var zeta = (2306.2181 * T + 0.30188 * T * T + 0.017998 * T * T * T) * AS, z = (2306.2181 * T + 1.09468 * T * T + 0.018203 * T * T * T) * AS,
          th = (2004.3109 * T - 0.42665 * T * T - 0.041833 * T * T * T) * AS, ct = Math.cos(th), st = Math.sin(th);
      for (i = 0; i < n; i++) {
        j = i * 6;
        var d0 = s[j + 1] / 1000 * DEG, d = Math.max(-89.9999, Math.min(89.9999, s[j + 1] / 1000 + s[j + 5] / 3600000 * yrs)) * DEG;
        var a = (s[j] / 1000 + s[j + 4] / 3600000 * yrs / Math.cos(d0)) * DEG + zeta, cd = Math.cos(d);
        var A = cd * Math.sin(a), B = ct * cd * Math.cos(a) - st * Math.sin(d), C = st * cd * Math.cos(a) + ct * Math.sin(d);
        k.ra[i] = rev((Math.atan2(A, B) + z) / DEG); k.lat[i] = Math.asin(Math.max(-1, Math.min(1, C))) / DEG;
      }
      k.at = ms;
    }
    var g = turn(ms);
    for (i = 0; i < n; i++) k.lon[i] = rev(k.ra[i] - g + 180) - 180;
    return k;
  }

  // ---------------------------------------------------------------- the sky drawn, from a place
  // Both drawings show what the eye is left: the sky is as light as the sun makes it, no star by day, the brightest
  // in twilight, all of them once the sun is twelve degrees down. Both say what they drew: how many stars, whether it
  // is day, twilight or night, and - north of the equator - which named star stands nearest the pole of the sky.
  function tint(bv) { return bv < 0 ? '#b9ccff' : bv < 0.3 ? '#dbe6ff' : bv < 0.62 ? '#fbf6ee' : bv < 1 ? '#ffe7bf' : bv < 1.4 ? '#ffd29a' : '#ffbc84'; }
  function faintest(sunUp) { return sunUp > -1 ? -9 : Math.min(5, 1.5 + (-sunUp - 6) * 0.5); }
  function light(sunUp) { return sunUp > -1 ? 'day' : sunUp > -12 ? 'twilight' : 'night'; }
  function nearPole(cat, k) {
    var best = null;
    Object.keys(cat.names).forEach(function (j) { var off = 90 - k.lat[+j]; if (!best || off < best.off) best = {name: cat.names[j], off: off}; });
    return best;
  }
  function blue(f, a, b) { return 'rgb(' + Math.round(a[0] + (b[0] - a[0]) * f) + ',' + Math.round(a[1] + (b[1] - a[1]) * f) + ',' + Math.round(a[2] + (b[2] - a[2]) * f) + ')'; }

  // The whole sky as a round chart - the way it is seen lying on your back with your head to the north. size is the
  // canvas's own width. The moon is drawn larger than it is.
  function dome(g, size, at, ms, cat) {
    var l = look(at, ms), u = size / 300, c = size / 2, Rd = 132 * u, sunUp = l.sun.up, f = Math.max(0, Math.min(1, (sunUp + 12) / 12));
    var out = {stars: 0, pole: null, light: light(sunUp), look: l}, lim = faintest(sunUp), named = 0, q, i;
    function spot(up, way) { var r = Rd * (90 - Math.max(0, up)) / 90; return {x: c - r * Math.sin(way * DEG), y: c - r * Math.cos(way * DEG)}; }
    g.clearRect(0, 0, size, size);
    g.beginPath(); g.arc(c, c, Rd, 0, 7); g.fillStyle = blue(f * f, [7, 11, 18], [52, 98, 150]); g.fill();
    if (cat) {
      var k = stars(cat, ms);
      g.font = Math.round(10 * u) + "px 'Courier New',monospace"; g.textBaseline = 'middle';
      for (i = 0; i < k.n && k.mag[i] <= lim; i++) {                   // brightest first: stop at the faintest the light leaves
        var st = {lat: k.lat[i], lon: k.lon[i]}, up = 90 - apart(at, st);
        if (up < 0) continue;
        q = spot(up, bearing(at, st)); out.stars++;
        g.globalAlpha = Math.max(0.35, Math.min(1, 1.05 - 0.15 * k.mag[i])); g.fillStyle = tint(k.bv[i]);
        g.beginPath(); g.arc(q.x, q.y, Math.max(0.7, 2.7 - 0.42 * k.mag[i]) * u, 0, 7); g.fill();
        if (cat.names[i] && named < 5 && up > 8) { named++; g.globalAlpha = 0.75; g.fillStyle = '#8395a7'; g.textAlign = q.x > c ? 'right' : 'left'; g.fillText(cat.names[i], q.x + (q.x > c ? -5 : 5) * u, q.y); }
      }
      g.globalAlpha = 1;
      if (at.lat > 0) {                                               // the pole of the sky stands as high as the place is far north, due north
        q = spot(at.lat, 0); g.strokeStyle = 'rgba(46,204,113,.8)'; g.lineWidth = u;
        g.beginPath(); g.moveTo(q.x - 5 * u, q.y); g.lineTo(q.x + 5 * u, q.y); g.moveTo(q.x, q.y - 5 * u); g.lineTo(q.x, q.y + 5 * u); g.stroke();
        out.pole = nearPole(cat, k);
      }
    }
    if (sunUp > -0.9) {
      q = spot(sunUp, l.sun.way);
      g.beginPath(); g.arc(q.x, q.y, 14 * u, 0, 7); g.fillStyle = 'rgba(255,214,102,.25)'; g.fill();
      g.beginPath(); g.arc(q.x, q.y, 6.5 * u, 0, 7); g.fillStyle = '#ffd666'; g.fill();
    }
    if (l.moon.up > -0.5) { q = spot(l.moon.up, l.moon.way); moonFace(g, q.x, q.y, 8 * u, l.lit, l.moon.tilt + 180 - l.moon.way, '#2a323d', '#eef1f5'); }
    g.beginPath(); g.arc(c, c, Rd, 0, 7); g.strokeStyle = 'rgba(131,149,167,.6)'; g.lineWidth = u; g.stroke();
    g.fillStyle = '#8395a7'; g.font = Math.round(11 * u) + "px 'Courier New',monospace"; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText('N', c, c - Rd - 9 * u); g.fillText('S', c, c + Rd + 9 * u); g.fillText('E', c - Rd - 9 * u, c); g.fillText('W', c + Rd + 9 * u, c);
    return out;
  }

  // The same sky as a strip all the way round: north at the left edge, then east, south in the middle, west, and
  // north again at the right edge - what is seen turning once round on the spot, facing south at the start. The
  // horizon is `ground` pixels above the foot of the picture and the top edge is straight overhead. w and h are in
  // the units the context draws in. With opt.moon false the moon is left out, and where it stands is given back so
  // the page can put its own moon there. opt.letters 'above' writes N E S W over the horizon instead of under it.
  // opt.dark takes the daylight away: every star that is up is drawn whatever the hour, the sun among them, and what
  // is given back still says whether it is day - a night sky is there all day, behind the light.
  function round(g, w, h, at, ms, cat, opt) {
    opt = opt || {};
    var l = look(at, ms), ground = opt.ground == null ? 26 : opt.ground, floor = h - ground, sunUp = l.sun.up, f = opt.dark ? 0 : Math.max(0, Math.min(1, (sunUp + 12) / 12));
    var out = {stars: 0, pole: null, light: light(sunUp), look: l, sun: null, moon: null, floor: floor}, lim = opt.dark ? 5 : faintest(sunUp), named = 0, q, i;
    function spot(up, way) { return {x: ((way % 360) + 360) % 360 / 360 * w, y: floor - Math.max(0, up) / 90 * floor}; }
    g.clearRect(0, 0, w, h);
    var sk = g.createLinearGradient(0, 0, 0, floor);
    sk.addColorStop(0, blue(f * f, [2, 3, 5], [38, 84, 140])); sk.addColorStop(1, blue(f * f, [11, 21, 34], [96, 146, 196]));
    g.fillStyle = sk; g.fillRect(0, 0, w, floor);
    if (!opt.dark && sunUp > -14 && sunUp < 4) {                      // the glow over where the sun is, at dawn and at dusk
      q = spot(0, l.sun.way);
      [q.x - w, q.x, q.x + w].forEach(function (x) {
        var gl = g.createRadialGradient(x, floor, 0, x, floor, w * 0.22);
        gl.addColorStop(0, 'rgba(255,170,96,' + (0.5 * (1 - Math.abs(sunUp + 3) / 11)).toFixed(3) + ')'); gl.addColorStop(1, 'rgba(255,170,96,0)');
        g.fillStyle = gl; g.fillRect(0, 0, w, floor);
      });
    }
    if (cat) {
      var k = stars(cat, ms);
      g.font = "10px 'Courier New',monospace"; g.textBaseline = 'middle';
      for (i = 0; i < k.n && k.mag[i] <= lim; i++) {
        var st = {lat: k.lat[i], lon: k.lon[i]}, up = 90 - apart(at, st);
        if (up < 0) continue;
        q = spot(up, bearing(at, st)); out.stars++;
        g.globalAlpha = Math.max(0.35, Math.min(1, 1.05 - 0.15 * k.mag[i])); g.fillStyle = tint(k.bv[i]);
        g.beginPath(); g.arc(q.x, q.y, Math.max(0.6, 2.4 - 0.38 * k.mag[i]), 0, 7); g.fill();
        if (cat.names[i] && named < 7 && up > 6 && up < 80 && q.x > 30 && q.x < w - 70) { named++; g.globalAlpha = 0.7; g.fillStyle = '#8395a7'; g.textAlign = 'left'; g.fillText(cat.names[i], q.x + 6, q.y); }
      }
      g.globalAlpha = 1;
      if (at.lat > 0) {
        out.pole = nearPole(cat, k); q = spot(at.lat, 0);
        g.strokeStyle = 'rgba(46,204,113,.8)'; g.lineWidth = 1;
        [q.x + 6, w - 6].forEach(function (x) { g.beginPath(); g.moveTo(x - 5, q.y); g.lineTo(x + 5, q.y); g.moveTo(x, q.y - 5); g.lineTo(x, q.y + 5); g.stroke(); });
      }
    }
    if (sunUp > -0.9) {
      q = out.sun = spot(sunUp, l.sun.way);
      g.beginPath(); g.arc(q.x, q.y, 20, 0, 7); g.fillStyle = 'rgba(255,214,102,.25)'; g.fill();
      g.beginPath(); g.arc(q.x, q.y, 9, 0, 7); g.fillStyle = '#ffd666'; g.fill();
    }
    if (l.moon.up > -0.5) {
      q = out.moon = spot(l.moon.up, l.moon.way);
      if (opt.moon !== false) moonFace(g, q.x, q.y, 11, l.lit, l.moon.tilt, '#2a323d', '#eef1f5');
    }
    g.fillStyle = 'rgba(4,6,9,.92)'; g.fillRect(0, floor, w, ground);                  // the ground
    g.strokeStyle = 'rgba(131,149,167,.45)'; g.lineWidth = 1; g.beginPath(); g.moveTo(0, floor + 0.5); g.lineTo(w, floor + 0.5); g.stroke();
    if (ground >= 14 || opt.letters === 'above') {
      g.fillStyle = '#8395a7'; g.font = "10px 'Courier New',monospace"; g.textBaseline = 'middle';
      [['N', 0, 'left'], ['E', 0.25, 'center'], ['S', 0.5, 'center'], ['W', 0.75, 'center'], ['N', 1, 'right']].forEach(function (c) { g.textAlign = c[2]; g.fillText(c[0], c[1] * w + (c[1] === 0 ? 6 : c[1] === 1 ? -6 : 0), opt.letters === 'above' ? floor - 9 : floor + Math.min(ground, 26) / 2 + 1); });
    }
    return out;
  }

  // ---------------------------------------------------------------- dates
  function jdn(y, m, d, old) {                                        // the day number at noon of a calendar day
    var a = Math.floor((14 - m) / 12), yy = y + 4800 - a, mm = m + 12 * a - 3;
    var n = d + Math.floor((153 * mm + 2) / 5) + 365 * yy + Math.floor(yy / 4);
    return old ? n - 32083 : n - Math.floor(yy / 100) + Math.floor(yy / 400) - 32045;
  }
  function of(y, m, d, h, min, style) {                               // a calendar date and a UT time of day -> ms
    var old = style ? style === 'old' : (y < 1582 || (y === 1582 && (m < 10 || (m === 10 && d < 15))));
    return (jdn(y, m, d, old) - 2440588) * DAY + ((h || 0) * 60 + (min || 0)) * 60000;
  }
  function cal(ms) {                                                  // ms -> the calendar date as it was written then
    var old = ms < REFORM, z = Math.floor(ms / DAY) + 2440588, a = z, al;
    if (!old) { al = Math.floor((z - 1867216.25) / 36524.25); a = z + 1 + al - Math.floor(al / 4); }
    var b = a + 1524, c = Math.floor((b - 122.1) / 365.25), dd = Math.floor(365.25 * c), e = Math.floor((b - dd) / 30.6001);
    var day = b - dd - Math.floor(30.6001 * e), m = e < 14 ? e - 1 : e - 13, y = m > 2 ? c - 4716 : c - 4715;
    var rest = ms - Math.floor(ms / DAY) * DAY;
    return {y: y, m: m, d: day, h: Math.floor(rest / 3600000), min: Math.floor(rest % 3600000 / 60000), old: old, weekday: ((z + 1) % 7 + 7) % 7};
  }
  function two(n) { return (n < 10 ? '0' : '') + n; }
  function year(y) { return y > 0 ? (y < 1000 ? 'AD ' + y : String(y)) : (1 - y) + ' BC'; }
  function stamp(ms, brief) {                                         // for people: "AD 824 Apr 3 05:41 UT · old calendar"
    var c = cal(ms);
    return year(c.y) + ' ' + MONTHS[c.m - 1] + ' ' + c.d + ' ' + two(c.h) + ':' + two(c.min) + ' UT' + (c.old && !brief ? ' · old calendar' : '');
  }
  function mark(ms) {                                                 // for an address: 0824-04-03T05:41, in the same calendar as stamp
    var c = cal(ms), y = Math.abs(c.y);
    return (c.y < 0 ? '-' : '') + (y < 10 ? '000' : y < 100 ? '00' : y < 1000 ? '0' : '') + y + '-' + two(c.m) + '-' + two(c.d) + 'T' + two(c.h) + ':' + two(c.min);
  }
  function read(text) {                                               // "824-04-03 05:41", "0824-04-03T05:41", "824", "-45-03-15" -> ms, or null
    var m = /^\s*(-?\d{1,4})(?:-(\d{1,2})(?:-(\d{1,2})(?:[T\s]+(\d{1,2})(?::(\d{2}))?)?)?)?\s*(?:UT|Z)?\s*$/i.exec(String(text));
    if (!m) return null;
    var y = +m[1], mo = m[2] ? +m[2] : 1, d = m[3] ? +m[3] : 1, h = m[4] ? +m[4] : 12, mi = m[5] ? +m[5] : 0;
    if (mo < 1 || mo > 12 || d < 1 || d > 31 || h > 23 || mi > 59 || y < -2999 || y > 2999) return null;
    return of(y, mo, d, h, mi);
  }
  function easter(y) {                                                // Easter Sunday at 0h UT
    var a, b, c, d, e;
    if (y < 1583) { a = y % 4; b = y % 7; c = y % 19; d = (19 * c + 15) % 30; e = (2 * a + 4 * b - d + 34) % 7; return of(y, Math.floor((d + e + 114) / 31), (d + e + 114) % 31 + 1, 0, 0, 'old'); }
    a = y % 19; b = Math.floor(y / 100); c = y % 100; d = Math.floor(b / 4); e = b % 4;
    var f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4;
    var l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451);
    return of(y, Math.floor((h + l - 7 * m + 114) / 31), (h + l - 7 * m + 114) % 31 + 1, 0, 0, 'new');
  }

  sky.look = look; sky.next = next; sky.moonFace = moonFace; sky.moonName = moonName; sky.apart = apart; sky.bearing = bearing;
  sky.stars = stars; sky.turn = turn; sky.dome = dome; sky.round = round; sky.tint = tint;
  sky.deltaT = deltaT; sky.of = of; sky.cal = cal; sky.stamp = stamp; sky.mark = mark; sky.read = read; sky.easter = easter;
  sky.FIRST = of(-2999, 1, 1, 0, 0); sky.LAST = of(2999, 12, 31, 0, 0);     // as far as the fit for the earth's turning is given
  root.gaiaSky = sky;
  if (typeof module !== 'undefined' && module.exports) module.exports = sky;
})(typeof window !== 'undefined' ? window : globalThis);
