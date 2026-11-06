/* localize.js — geographic localization.
 * Maps visitor timezone/locale to tuebor geographic zones.
 * No IP geolocation. Timezone + language only. Consent-based. */
(function(){
  "use strict";
  function detect() {
    var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    var lang = navigator.language || "en";
    var zone = "globe";
    if (tz.includes("America/Detroit") || tz.includes("America/New_York")) zone = "michigan";
    else if (tz.includes("America/Chicago")) zone = "midwest";
    else if (tz.includes("America/")) zone = "us";
    else if (tz.includes("Europe/")) zone = "europe";
    else if (tz.includes("Asia/")) zone = "asia";
    else if (tz.includes("Australia/")) zone = "oceania";
    document.body.setAttribute("data-locale-zone", zone);
    document.body.setAttribute("data-locale-lang", lang.slice(0,2));
    return { zone: zone, lang: lang, tz: tz };
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", detect);
  else detect();
  window.Localize = { detect: detect };
})();
