/*
  Links auf fremde Websites öffnen in einem neuen Tab, damit cogneon.de offen
  bleibt. Gilt für alle http(s)-Links, deren Ziel nicht cogneon.de ist, auch
  für Inhalte, die erst später erscheinen (Kommentare). Screenreader hören den
  Zusatz "(öffnet in neuem Tab)". Mailto-, Telefon- und interne Links bleiben
  unverändert.
*/
(function () {
  "use strict";

  var EIGEN = ["cogneon.de", "www.cogneon.de", location.hostname];
  var HINWEIS = document.documentElement.lang === "en" ? " (opens in new tab)" : " (öffnet in neuem Tab)";

  function extern(a) {
    if (!a || !/^https?:$/.test(a.protocol)) return false;
    return EIGEN.indexOf(a.hostname) < 0;
  }

  function markieren(a) {
    if (a.dataset.cgExtern) return;
    a.dataset.cgExtern = "1";
    if (!a.target) a.target = "_blank";
    var rel = (a.getAttribute("rel") || "").split(/\s+/).filter(Boolean);
    if (rel.indexOf("noopener") < 0) rel.push("noopener");
    a.setAttribute("rel", rel.join(" "));
    var sr = document.createElement("span");
    sr.className = "cg-sr";
    sr.textContent = HINWEIS;
    a.appendChild(sr);
  }

  function alle() {
    document.querySelectorAll("a[href]").forEach(function (a) {
      if (extern(a)) markieren(a);
    });
  }

  // Auch Links, die nach dem Laden entstehen, rechtzeitig vor dem Klick markieren.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (extern(a)) markieren(a);
  }, true);

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(alle);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", alle);
  } else {
    alle();
  }
})();
