/*
  Adventskalender /advent/: glühendes Netz hinter den Türchen; ein Klick klappt
  ein Türchen auf und zeigt seinen Inhalt in einem Dialog. Ohne JavaScript
  bleibt der Hintergrund dunkel und die Türchen springen zur Liste darunter.

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
  // --- Türchen öffnen -----------------------------------------------------
  // Ein Klick klappt das Türchen auf und zeigt seinen Inhalt in einem Dialog.
  // Ohne JavaScript oder ohne <dialog> springt der Link zur Liste darunter.
  var ruhig = window.matchMedia("(prefers-reduced-motion: reduce)");
  var dialog = document.querySelector(".cg-advent__dialog");
  var tueren = Array.prototype.slice.call(document.querySelectorAll(".cg-tuer--offen"));
  var KLAPPEN = 320; // ms, passend zu advent.css

  if (dialog && typeof dialog.showModal === "function" && tueren.length) {
    var inhalt = dialog.querySelector(".cg-advent__dialog-inhalt");
    var ausloeser = null;

    function tuerZu(id) {
      for (var i = 0; i < tueren.length; i++) if (tueren[i].getAttribute("href") === "#" + id) return tueren[i];
      return null;
    }

    function oeffnen(id, tuer, animiert) {
      var quelle = document.getElementById(id);
      if (!quelle || id.indexOf("tag-") !== 0) return;
      var kopie = quelle.cloneNode(true);
      kopie.removeAttribute("id");
      kopie.removeAttribute("aria-labelledby");
      kopie.className = "cg-advent__dialog-eintrag";
      var h = kopie.querySelector("h3");
      if (h) { h.id = "advent-dialog-titel"; }
      inhalt.innerHTML = "";
      inhalt.appendChild(kopie);
      ausloeser = tuer || tuerZu(id);
      if (history.replaceState) history.replaceState(null, "", "#" + id);

      function zeigen() {
        dialog.showModal();
        dialog.querySelector(".cg-advent__schliessen").focus();
      }
      if (animiert && ausloeser && !ruhig.matches) {
        ausloeser.classList.add("cg-tuer--klappt");
        setTimeout(zeigen, KLAPPEN);
      } else {
        zeigen();
      }
    }

    function schliessen() { if (dialog.open) dialog.close(); }

    dialog.addEventListener("close", function () {
      if (history.replaceState) history.replaceState(null, "", location.pathname + location.search);
      if (ausloeser) {
        ausloeser.classList.remove("cg-tuer--klappt");
        ausloeser.focus();
      }
    });
    // Klick auf den abgedunkelten Rand schließt.
    dialog.addEventListener("click", function (ev) { if (ev.target === dialog) schliessen(); });
    dialog.querySelector(".cg-advent__schliessen").addEventListener("click", schliessen);

    tueren.forEach(function (t) {
      t.addEventListener("click", function (ev) {
        ev.preventDefault();
        oeffnen(t.getAttribute("href").slice(1), t, true);
      });
    });

    // Direktlink /advent/#tag-5 öffnet das Türchen sofort.
    // Der Browser springt dabei zur Liste; zurück zum Kalender, damit er hinter dem Dialog steht.
    var start = location.hash.slice(1);
    if (start && document.getElementById(start)) {
      var direkt = function () {
        var kalender = document.querySelector(".cg-advent");
        if (kalender) window.scrollTo(0, kalender.getBoundingClientRect().top + window.pageYOffset);
        oeffnen(start, null, false);
      };
      // Erst nach dem Sprung des Browsers zum Anker, sonst springt er hinterher.
      if (document.readyState === "complete") setTimeout(direkt, 0);
      else window.addEventListener("load", function () { setTimeout(direkt, 0); });
    }
    window.addEventListener("hashchange", function () {
      var id = location.hash.slice(1);
      if (id && !dialog.open) oeffnen(id, null, false);
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
