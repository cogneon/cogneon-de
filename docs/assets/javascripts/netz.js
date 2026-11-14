/*
  Netz im dunklen Einstieg der Startseite: Neuronen driften langsam,
  ab und zu läuft ein Geistesblitz an einer Verbindung entlang.

  Stellschrauben: */
var NETZ = {
  dichte: 1,          // 1 = Standard, 0.5 = halb so viele Punkte, 1.5 = mehr
  tempo: 1,           // Driftgeschwindigkeit der Punkte
  blitzAbstand: 2800, // mittlere Zeit zwischen zwei Geistesblitzen in ms
  blitzFarbe: "255, 102, 0",   // Orange #ff6600, als "r, g, b"
  linienDeckkraft: 0.09,       // Deckkraft der Verbindungen (0 bis 1)
  punktDeckkraft: 0.28         // Deckkraft der Punkte (0 bis 1)
};
/* Ende der Stellschrauben. */

(function () {
  var huelle = document.querySelector(".cg-netz");
  if (!huelle) return;
  var canvas = huelle.querySelector("canvas");
  var knopf = document.querySelector(".cg-netz__pause");
  var ctx = canvas.getContext("2d");
  var ruhig = window.matchMedia("(prefers-reduced-motion: reduce)");

  var punkte = [], kanten = [], blitze = [];
  var breite = 0, hoehe = 0, dpr = 1, reichweite = 0;
  var laeuft = false, pausiert = false, sichtbar = true, naechsterBlitz = 0, letzte = 0, frame = 0;

  function zufall(a, b) { return a + Math.random() * (b - a); }

  // Deckkraft je nach horizontaler Lage: links hinter dem Claim fast unsichtbar.
  function maske(x) {
    var t = x / breite;
    return 0.15 + 0.85 * Math.min(1, Math.max(0, (t - 0.15) / 0.55));
  }

  function aufbauen() {
    var r = huelle.getBoundingClientRect();
    breite = r.width; hoehe = r.height;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(breite * dpr);
    canvas.height = Math.round(hoehe * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    reichweite = Math.max(110, Math.min(180, breite / 9));
    var anzahl = Math.round(Math.min(90, Math.max(28, breite * hoehe / 16000)) * NETZ.dichte);
    punkte = [];
    for (var i = 0; i < anzahl; i++) {
      var w = zufall(0, Math.PI * 2), v = zufall(0.04, 0.12) * NETZ.tempo;
      punkte.push({ x: zufall(0, breite), y: zufall(0, hoehe), vx: Math.cos(w) * v, vy: Math.sin(w) * v,
                    r: zufall(1, 2.2), glut: 0 });
    }
    blitze = [];
  }

  function bewegen(dt) {
    for (var i = 0; i < punkte.length; i++) {
      var p = punkte[i];
      p.x += p.vx * dt / 16; p.y += p.vy * dt / 16;
      if (p.x < -20) p.x = breite + 20; else if (p.x > breite + 20) p.x = -20;
      if (p.y < -20) p.y = hoehe + 20; else if (p.y > hoehe + 20) p.y = -20;
      p.glut = Math.max(0, p.glut - dt / 900);
    }
  }

  function nachbarn(i) {
    var a = punkte[i], liste = [];
    for (var j = 0; j < punkte.length; j++) {
      if (j === i) continue;
      var dx = punkte[j].x - a.x, dy = punkte[j].y - a.y;
      if (dx * dx + dy * dy < reichweite * reichweite) liste.push(j);
    }
    return liste;
  }

  function blitzStarten(von, tiefe) {
    var n = nachbarn(von);
    if (!n.length) return;
    var nach = n[Math.floor(Math.random() * n.length)];
    blitze.push({ von: von, nach: nach, t: 0, tiefe: tiefe });
    punkte[von].glut = Math.max(punkte[von].glut, 0.6);
  }

  function blitzeFortschreiben(dt) {
    for (var i = blitze.length - 1; i >= 0; i--) {
      var b = blitze[i];
      b.t += dt / 650;
      if (b.t >= 1) {
        punkte[b.nach].glut = 1;
        blitze.splice(i, 1);
        // Kleine Kettenreaktion: manchmal geht der Impuls weiter.
        if (b.tiefe < 3 && Math.random() < 0.55) blitzStarten(b.nach, b.tiefe + 1);
        if (b.tiefe < 2 && Math.random() < 0.2) blitzStarten(b.nach, b.tiefe + 1);
      }
    }
  }

  function zeichnen() {
    ctx.clearRect(0, 0, breite, hoehe);
    var r2 = reichweite * reichweite;
    ctx.lineWidth = 1;
    for (var i = 0; i < punkte.length; i++) {
      var a = punkte[i];
      for (var j = i + 1; j < punkte.length; j++) {
        var b = punkte[j], dx = b.x - a.x, dy = b.y - a.y, d2 = dx * dx + dy * dy;
        if (d2 > r2) continue;
        var alpha = NETZ.linienDeckkraft * (1 - d2 / r2) * maske((a.x + b.x) / 2);
        ctx.strokeStyle = "rgba(255,255,255," + alpha.toFixed(3) + ")";
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
    }
    for (var k = 0; k < blitze.length; k++) {
      var bl = blitze[k], p = punkte[bl.von], q = punkte[bl.nach];
      var x = p.x + (q.x - p.x) * bl.t, y = p.y + (q.y - p.y) * bl.t;
      var m = maske(x);
      var spur = ctx.createLinearGradient(p.x, p.y, x, y);
      spur.addColorStop(0, "rgba(" + NETZ.blitzFarbe + ",0)");
      spur.addColorStop(1, "rgba(" + NETZ.blitzFarbe + "," + (0.55 * m).toFixed(3) + ")");
      ctx.strokeStyle = spur; ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(x, y); ctx.stroke();
      ctx.fillStyle = "rgba(" + NETZ.blitzFarbe + "," + (0.9 * m).toFixed(3) + ")";
      ctx.beginPath(); ctx.arc(x, y, 1.8, 0, Math.PI * 2); ctx.fill();
    }
    for (var n = 0; n < punkte.length; n++) {
      var pt = punkte[n], mm = maske(pt.x);
      if (pt.glut > 0) {
        var g = ctx.createRadialGradient(pt.x, pt.y, 0, pt.x, pt.y, 14);
        g.addColorStop(0, "rgba(" + NETZ.blitzFarbe + "," + (0.45 * pt.glut * mm).toFixed(3) + ")");
        g.addColorStop(1, "rgba(" + NETZ.blitzFarbe + ",0)");
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, 14, 0, Math.PI * 2); ctx.fill();
      }
      ctx.fillStyle = "rgba(255,255,255," + (NETZ.punktDeckkraft * mm).toFixed(3) + ")";
      ctx.beginPath(); ctx.arc(pt.x, pt.y, pt.r, 0, Math.PI * 2); ctx.fill();
    }
  }

  function schritt(zeit) {
    if (!laeuft) return;
    var dt = Math.min(64, zeit - (letzte || zeit));
    letzte = zeit;
    bewegen(dt);
    if (zeit > naechsterBlitz) {
      // Blitze bevorzugt rechts, wo das Netz sichtbar ist.
      var kandidaten = punkte.map(function (p, i) { return i; }).filter(function (i) { return punkte[i].x > breite * 0.4; });
      if (kandidaten.length) blitzStarten(kandidaten[Math.floor(Math.random() * kandidaten.length)], 0);
      naechsterBlitz = zeit + NETZ.blitzAbstand * zufall(0.6, 1.4);
    }
    blitzeFortschreiben(dt);
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

  aufbauen();
  zeichnen();   // Standbild, auch bei "Bewegung reduzieren"
  huelle.classList.add("cg-netz--bereit");

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (e) { sichtbar = e[0].isIntersecting; steuern(); }).observe(huelle);
  }
  document.addEventListener("visibilitychange", steuern);
  if (ruhig.addEventListener) ruhig.addEventListener("change", steuern);
  if (knopf) knopf.addEventListener("click", function () {
    pausiert = !pausiert;
    try { localStorage.setItem("cg-netz-pause", pausiert ? "1" : "0"); } catch (e) {}
    steuern();
  });
  try { pausiert = localStorage.getItem("cg-netz-pause") === "1"; } catch (e) {}

  var timer;
  window.addEventListener("resize", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { aufbauen(); zeichnen(); }, 200);
  });
  steuern();
})();
