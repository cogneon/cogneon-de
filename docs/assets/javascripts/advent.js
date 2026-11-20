/*
  Adventskalender /advent/: glühendes Netz hinter den Türchen und Anzeige des
  gewählten Türchens. Ohne JavaScript bleibt der Hintergrund dunkel und alle
  offenen Türchen stehen als Liste da.

  Stellschrauben: */
var ADVENT = {
  dichte: 1,          // 1 = Standard, 0.5 = halb so viele Lichter
  tempo: 1,           // Driftgeschwindigkeit
  helligkeit: 0.9,    // Gesamthelligkeit des Netzes (0 bis 1), gedämpft hinter den Türchen
  pulsAbstand: 3200,  // mittlere Zeit zwischen zwei Lichtwellen in ms
  farbe: [255, 120, 30]
};
/* Ende der Stellschrauben. */

(function () {
  // --- Türchen-Auswahl -----------------------------------------------------
  var eintraege = Array.prototype.slice.call(document.querySelectorAll(".cg-advent__eintrag"));
  var tueren = Array.prototype.slice.call(document.querySelectorAll(".cg-tuer--offen"));
  var alle = document.querySelector(".cg-advent__alle");
  var ruhig = window.matchMedia("(prefers-reduced-motion: reduce)");

  function zeigen(id, fokus) {
    var treffer = false;
    eintraege.forEach(function (e) {
      var an = !id || e.id === id;
      e.hidden = !an;
      if (e.id === id) treffer = true;
    });
    if (id && !treffer) { zeigen(null, false); return; }
    tueren.forEach(function (t) {
      t.classList.toggle("cg-tuer--aktiv", !!id && t.getAttribute("href") === "#" + id);
    });
    if (alle) alle.hidden = !id || eintraege.length < 2;
    if (id && fokus) {
      var titel = document.getElementById(id + "-titel");
      var ziel = document.getElementById(id);
      if (ziel) ziel.scrollIntoView({ behavior: ruhig.matches ? "auto" : "smooth", block: "center" });
      if (titel) titel.focus({ preventScroll: true });
    }
  }

  if (eintraege.length) {
    var start = location.hash.slice(1);
    // Standard: das neueste offene Türchen (steht zuerst in der Liste).
    zeigen(start && document.getElementById(start) ? start : eintraege[0].id, !!start);
    tueren.forEach(function (t) {
      t.addEventListener("click", function (ev) {
        ev.preventDefault();
        var id = t.getAttribute("href").slice(1);
        if (history.replaceState) history.replaceState(null, "", "#" + id);
        zeigen(id, true);
      });
    });
    window.addEventListener("hashchange", function () {
      var id = location.hash.slice(1);
      if (document.getElementById(id) && id.indexOf("tag-") === 0) zeigen(id, true);
    });
    var alleLink = alle && alle.querySelector("[data-alle]");
    if (alleLink) alleLink.addEventListener("click", function (ev) {
      ev.preventDefault();
      if (history.replaceState) history.replaceState(null, "", location.pathname);
      zeigen(null, false);
      eintraege[0].querySelector("h3").focus();
    });
  }

  // --- Netz ----------------------------------------------------------------
  var huelle = document.querySelector(".cg-advent__netz");
  if (!huelle) return;
  var canvas = huelle.querySelector("canvas");
  var ctx = canvas.getContext && canvas.getContext("2d");
  if (!ctx) return;
  var knopf = document.querySelector(".cg-advent__pause");
  var f = ADVENT.farbe.join(",");

  var lichter = [], wellen = [], breite = 0, hoehe = 0, dpr = 1, reichweite = 0;
  var laeuft = false, pausiert = false, sichtbar = true, letzte = 0, frame = 0, jetzt = 0, naechsterPuls = 1500;
  var glanz = null;

  function zufall(a, b) { return a + Math.random() * (b - a); }

  // Ein vorgezeichneter Lichthof, der nur noch skaliert wird: schont die CPU.
  function glanzBauen() {
    var g = document.createElement("canvas"), s = 64;
    g.width = g.height = s;
    var c = g.getContext("2d"), r = c.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
    r.addColorStop(0, "rgba(" + f + ",0.9)");
    r.addColorStop(0.25, "rgba(" + f + ",0.35)");
    r.addColorStop(1, "rgba(" + f + ",0)");
    c.fillStyle = r;
    c.fillRect(0, 0, s, s);
    glanz = g;
  }

  function aufbauen() {
    var r = huelle.getBoundingClientRect();
    breite = r.width; hoehe = r.height;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(breite * dpr);
    canvas.height = Math.round(hoehe * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    reichweite = Math.max(100, Math.min(170, breite / 8));
    var anzahl = Math.round(Math.min(80, Math.max(26, breite * hoehe / 15000)) * ADVENT.dichte);
    lichter = [];
    for (var i = 0; i < anzahl; i++) {
      var w = zufall(0, Math.PI * 2), v = zufall(0.05, 0.14) * ADVENT.tempo;
      lichter.push({ x: zufall(0, breite), y: zufall(0, hoehe), vx: Math.cos(w) * v, vy: Math.sin(w) * v,
                     r: zufall(1.5, 4), tiefe: zufall(0.3, 1), phase: zufall(0, Math.PI * 2), energie: 0 });
    }
    wellen = [];
  }

  function bewegen(dt) {
    for (var i = 0; i < lichter.length; i++) {
      var p = lichter[i];
      p.x += p.vx * dt / 16; p.y += p.vy * dt / 16;
      if (p.x < -30) p.x = breite + 30; else if (p.x > breite + 30) p.x = -30;
      if (p.y < -30) p.y = hoehe + 30; else if (p.y > hoehe + 30) p.y = -30;
      p.energie = Math.max(0, p.energie - dt / 1400);
    }
    for (var k = wellen.length - 1; k >= 0; k--) {
      var w = wellen[k];
      w.r += dt * 0.18;
      for (var j = 0; j < lichter.length; j++) {
        var q = lichter[j], d = Math.hypot(q.x - w.x, q.y - w.y);
        if (Math.abs(d - w.r) < 14) q.energie = Math.min(1, q.energie + 0.5);
      }
      if (w.r > Math.max(breite, hoehe) * 0.6) wellen.splice(k, 1);
    }
  }

  function zeichnen() {
    var h = ADVENT.helligkeit;
    ctx.clearRect(0, 0, breite, hoehe);
    ctx.lineWidth = 0.6;
    for (var i = 0; i < lichter.length; i++) {
      for (var j = i + 1; j < lichter.length; j++) {
        var a = lichter[i], b = lichter[j], dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy;
        if (d2 > reichweite * reichweite) continue;
        var nah = 1 - Math.sqrt(d2) / reichweite;
        var al = (0.1 + 0.4 * Math.max(a.energie, b.energie)) * nah * h;
        ctx.strokeStyle = "rgba(" + f + "," + al.toFixed(3) + ")";
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
    }
    for (var n = 0; n < lichter.length; n++) {
      var p = lichter[n];
      var puls = 0.5 + 0.5 * Math.sin(jetzt / 900 + p.phase);
      var hof = p.r * (7 + 4 * puls + 10 * p.energie);
      ctx.globalAlpha = Math.min(1, (0.25 + 0.35 * p.tiefe + 0.5 * p.energie) * h);
      ctx.drawImage(glanz, p.x - hof, p.y - hof, hof * 2, hof * 2);
      ctx.globalAlpha = 1;
      ctx.fillStyle = "rgba(255,226,200," + ((0.45 + 0.4 * p.tiefe) * h).toFixed(3) + ")";
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r * 0.7, 0, Math.PI * 2); ctx.fill();
    }
  }

  function schritt(zeit) {
    if (!laeuft) return;
    var dt = Math.min(64, zeit - (letzte || zeit));
    letzte = zeit;
    jetzt += dt;
    if (jetzt > naechsterPuls && lichter.length) {
      var s = lichter[Math.floor(Math.random() * lichter.length)];
      wellen.push({ x: s.x, y: s.y, r: 0 });
      s.energie = 1;
      naechsterPuls = jetzt + ADVENT.pulsAbstand * zufall(0.6, 1.4);
    }
    bewegen(dt);
    zeichnen();
    frame = requestAnimationFrame(schritt);
  }

  function steuern() {
    var soll = sichtbar && !pausiert && !ruhig.matches && !document.hidden;
    if (soll && !laeuft) { laeuft = true; letzte = 0; frame = requestAnimationFrame(schritt); }
    if (!soll && laeuft) { laeuft = false; cancelAnimationFrame(frame); }
    if (knopf) {
      knopf.hidden = ruhig.matches;
      knopf.setAttribute("aria-pressed", pausiert ? "true" : "false");
      knopf.setAttribute("aria-label", pausiert ? "Animation fortsetzen" : "Animation anhalten");
    }
  }

  glanzBauen();
  aufbauen();
  zeichnen();   // Standbild, auch bei "Bewegung reduzieren"
  huelle.classList.add("cg-advent__netz--bereit");

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (e) { sichtbar = e[0].isIntersecting; steuern(); }).observe(huelle);
  }
  document.addEventListener("visibilitychange", steuern);
  if (ruhig.addEventListener) ruhig.addEventListener("change", steuern);
  if (knopf) knopf.addEventListener("click", function () { pausiert = !pausiert; steuern(); });

  var timer;
  window.addEventListener("resize", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { aufbauen(); zeichnen(); }, 200);
  });
  steuern();
})();
