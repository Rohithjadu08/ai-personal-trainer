// FITAI frontend configuration.
//
// The real backend base URL is injected at build time into config.generated.js
// (see build.js). This file provides safe localhost defaults for local dev and
// a single helper used across the app so there are NO hardcoded backend URLs.
(function () {
  window.FITAI_CONFIG = window.FITAI_CONFIG || {};

  if (!window.FITAI_CONFIG.API_BASE) {
    window.FITAI_CONFIG.API_BASE = "http://127.0.0.1:8000";
  }
  if (!window.FITAI_CONFIG.WS_BASE) {
    window.FITAI_CONFIG.WS_BASE = "ws://127.0.0.1:8000";
  }

  window.fitaiApiBase = function () {
    return window.FITAI_CONFIG.API_BASE;
  };

  window.fitaiWsBase = function () {
    return window.FITAI_CONFIG.WS_BASE;
  };
})();
