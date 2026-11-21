/*
  Karte mit Orten (OpenStreetMap), zum Beispiel auf der Kontaktseite.
  Einbinden im Markdown:  <div class="cg-karte"></div>
  Die Orte stehen in inhalte/karte.yml.

  Die Karte lädt erst nach einem Klick: Erst dann werden Kartenbilder von den
  Servern der OpenStreetMap Foundation abgerufen. Leaflet selbst liegt lokal.
  Das Luftbild (Bayerische Vermessungsverwaltung, CC BY 4.0) wird erst geladen,
  wenn jemand oben rechts auf "Luftbild" umschaltet. Darüber liegt dann die
  OSM-Karte halbdurchsichtig ("Straßen einblenden", abschaltbar).

  Zoomen: Plus/Minus, Doppelklick, Zwei-Finger-Geste auf Touchpad und Handy
  oder Strg + Mausrad. Mausrad allein scrollt weiter die Seite.
*/
(function () {
  var boxes = document.querySelectorAll(".cg-karte");
  if (!boxes.length) return;
  var base = document.querySelector('script[src*="karte.js"]').src.replace(/javascripts\/karte\.js.*$/, "");
  var FARBEN = { cogneon: "#ff6600", hotel: "#231f20", anreise: "#4a4647", sehenswert: "#8f8a8b" };
  // Texte je nach Sprache der Seite (<html lang>).
  var EN = (document.documentElement.lang || "").indexOf("en") === 0;
  var T = EN ? {
    hinweis: 'Clicking "Load map" loads map tiles from OpenStreetMap. Your IP address is transmitted to the OpenStreetMap Foundation. ' +
      "Aerial images are only loaded from the Bavarian Surveying Administration after switching.",
    laden: "Load map", oeffnen: "Open on OpenStreetMap", fehler: "The map could not be loaded.",
    mehr: "More", route: "Route", apple: "Apple Maps", karte: "Map", luftbild: "Aerial image",
    strassen: "Show streets", namen: { cogneon: "Cogneon", hotel: "Hotels", anreise: "Getting here", sehenswert: "Sights" }
  } : {
    hinweis: 'Mit Klick auf „Karte laden" werden Kartenbilder von OpenStreetMap geladen. ' +
      "Dabei wird eure IP-Adresse an die OpenStreetMap Foundation übertragen. " +
      "Das Luftbild kommt erst nach Umschalten von der Bayerischen Vermessungsverwaltung.",
    laden: "Karte laden", oeffnen: "Auf OpenStreetMap öffnen", fehler: "Die Karte ließ sich nicht laden.",
    mehr: "Mehr", route: "Route", apple: "Apple Karten", karte: "Karte", luftbild: "Luftbild",
    strassen: "Straßen einblenden", namen: { cogneon: "Cogneon", hotel: "Hotels", anreise: "Anreise", sehenswert: "Sehenswert" }
  };
  var NAMEN = T.namen;

  function laden(url, art) {
    return new Promise(function (ok, fehler) {
      var el = document.createElement(art === "css" ? "link" : "script");
      if (art === "css") { el.rel = "stylesheet"; el.href = url; } else { el.src = url; }
      el.onload = ok; el.onerror = fehler;
      document.head.appendChild(el);
    });
  }

  function text(s) {
    var d = document.createElement("div"); d.textContent = s || ""; return d.innerHTML;
  }

  // Links zur Routenplanung. Externe Dienste erst nach Klick auf den Link.
  function route(lat, lon) {
    var z = lat + "," + lon;
    return T.route + ': <a href="https://www.openstreetmap.org/directions?route=%3B' + encodeURIComponent(z) + '">OpenStreetMap</a> · ' +
      '<a href="https://www.google.com/maps/dir/?api=1&amp;destination=' + encodeURIComponent(z) + '">Google Maps</a> · ' +
      '<a href="https://maps.apple.com/?daddr=' + z + '">' + T.apple + "</a>";
  }

  // Zoomen mit Zwei-Finger-Geste: Chrome, Firefox und Edge melden sie als
  // Mausrad mit Strg-Taste, Safari als eigene "gesture"-Ereignisse. Normales
  // Scrollen bleibt bei der Seite.
  function zoomGesten(karte, el) {
    function punkt(ev) { return karte.mouseEventToContainerPoint(ev); }
    function grenzen(z) { return Math.max(karte.getMinZoom(), Math.min(karte.getMaxZoom(), z)); }
    el.addEventListener("wheel", function (ev) {
      if (!ev.ctrlKey) return;
      ev.preventDefault();
      var faktor = ev.deltaMode === 1 ? 0.05 : 0.01;
      karte.setZoomAround(punkt(ev), grenzen(karte.getZoom() - ev.deltaY * faktor), { animate: false });
    }, { passive: false });
    var start = null;
    el.addEventListener("gesturestart", function (ev) { ev.preventDefault(); start = karte.getZoom(); });
    el.addEventListener("gesturechange", function (ev) {
      if (start === null) return;
      ev.preventDefault();
      karte.setZoomAround(punkt(ev), grenzen(start + Math.log(ev.scale) / Math.LN2), { animate: false });
    });
    el.addEventListener("gestureend", function () { start = null; });
  }

  function zeigen(box) {
    box.classList.add("cg-karte--laedt");
    Promise.all([
      laden(base + "vendor/leaflet/leaflet.css", "css"),
      laden(base + "vendor/leaflet/leaflet.js", "js"),
      fetch(base + "karte/orte.json").then(function (r) { return r.json(); })
    ]).then(function (res) {
      var orte = res[2].orte || [];
      box.innerHTML = "";
      box.classList.remove("cg-karte--laedt");
      box.classList.add("cg-karte--aktiv");
      var flaeche = document.createElement("div");
      flaeche.className = "cg-karte__flaeche";
      box.appendChild(flaeche);
      var karte = L.map(flaeche, { scrollWheelZoom: false, zoomSnap: 0.25 });
      var osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende'
      }).addTo(karte);
      var luftbild = L.tileLayer("https://wmtsod{s}.bayernwolke.de/wmts/by_dop/smerc/{z}/{x}/{y}", {
        subdomains: "123456789",
        maxZoom: 19,
        attribution: 'Luftbild: <a href="https://geodaten.bayern.de/opengeodata/">Bayerische Vermessungsverwaltung</a> (CC BY 4.0)'
      });
      // Straßen über dem Luftbild: dieselbe OSM-Karte halbdurchsichtig darüber.
      var strassen = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19, opacity: 0.45, className: "cg-karte__strassen"
      });
      var basis = {}, ueber = {};
      basis[T.karte] = osm; basis[T.luftbild] = luftbild; ueber[T.strassen] = strassen;
      L.control.layers(basis, ueber,
        { collapsed: false }).addTo(karte);
      // Nach dem Klick ausführen, damit das Häkchen im Umschalter mitzieht.
      karte.on("baselayerchange", function (e) {
        setTimeout(function () {
          if (e.layer === luftbild && !karte.hasLayer(strassen)) karte.addLayer(strassen);
          if (e.layer === osm && karte.hasLayer(strassen)) karte.removeLayer(strassen);
        }, 0);
      });
      zoomGesten(karte, flaeche);
      var punkte = [], erstes = null;
      orte.forEach(function (o) {
        var gross = o.art === "cogneon";
        var m = L.circleMarker([o.lat, o.lon], {
          radius: gross ? 11 : 7, color: "#ffffff", weight: 2,
          fillColor: FARBEN[o.art] || "#4a4647", fillOpacity: 1
        }).addTo(karte);
        var html = "<strong>" + text(o.name) + "</strong>";
        if (o.text) html += "<br>" + text(o.text);
        if (o.link) html += '<br><a href="' + encodeURI(o.link) + '">' + T.mehr + "</a>";
        if (gross) html += "<br>" + route(o.lat, o.lon);
        m.bindPopup(html);
        if (gross) erstes = m;
        punkte.push([o.lat, o.lon]);
      });
      if (punkte.length) karte.fitBounds(punkte, { padding: [30, 30], maxZoom: 16 });
      if (erstes) erstes.openPopup();
      var arten = [];
      orte.forEach(function (o) { if (arten.indexOf(o.art) === -1) arten.push(o.art); });
      var legende = document.createElement("ul");
      legende.className = "cg-karte__legende";
      legende.innerHTML = arten.map(function (a) {
        return '<li><span style="background:' + (FARBEN[a] || "#4a4647") + '"></span>' + text(NAMEN[a] || a) + "</li>";
      }).join("");
      box.appendChild(legende);
    }).catch(function () {
      box.classList.remove("cg-karte--laedt");
      box.querySelector(".cg-karte__hinweis").textContent = T.fehler;
    });
  }

  boxes.forEach(function (box) {
    box.innerHTML =
      '<div class="cg-karte__vorschau">' +
      '<p class="cg-karte__hinweis">' + T.hinweis + "</p>" +
      '<p><button type="button" class="cg-button">' + T.laden + "</button> " +
      '<a class="cg-link" href="https://www.openstreetmap.org/node/3255611047">' + T.oeffnen + "</a></p></div>";
    box.querySelector("button").addEventListener("click", function () { zeigen(box); });
  });
})();
