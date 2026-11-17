/*
  Karte mit Orten (OpenStreetMap), zum Beispiel auf der Kontaktseite.
  Einbinden im Markdown:  <div class="cg-karte"></div>
  Die Orte stehen in inhalte/karte.yml.

  Die Karte lädt erst nach einem Klick: Erst dann werden Kartenbilder von den
  Servern der OpenStreetMap Foundation abgerufen. Leaflet selbst liegt lokal.
*/
(function () {
  var boxes = document.querySelectorAll(".cg-karte");
  if (!boxes.length) return;
  var base = document.querySelector('script[src*="karte.js"]').src.replace(/javascripts\/karte\.js.*$/, "");
  var FARBEN = { cogneon: "#ff6600", hotel: "#231f20", anreise: "#4a4647", sehenswert: "#8f8a8b" };
  var NAMEN = { cogneon: "Cogneon", hotel: "Hotels", anreise: "Anreise", sehenswert: "Sehenswert" };

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
      var karte = L.map(flaeche, { scrollWheelZoom: false });
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende'
      }).addTo(karte);
      var punkte = [], erstes = null;
      orte.forEach(function (o) {
        var gross = o.art === "cogneon";
        var m = L.circleMarker([o.lat, o.lon], {
          radius: gross ? 11 : 7, color: "#ffffff", weight: 2,
          fillColor: FARBEN[o.art] || "#4a4647", fillOpacity: 1
        }).addTo(karte);
        var html = "<strong>" + text(o.name) + "</strong>";
        if (o.text) html += "<br>" + text(o.text);
        if (o.link) html += '<br><a href="' + encodeURI(o.link) + '">Mehr</a>';
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
      box.querySelector(".cg-karte__hinweis").textContent = "Die Karte ließ sich nicht laden.";
    });
  }

  boxes.forEach(function (box) {
    box.innerHTML =
      '<div class="cg-karte__vorschau">' +
      '<p class="cg-karte__hinweis">Mit Klick auf „Karte laden" werden Kartenbilder von OpenStreetMap geladen. ' +
      'Dabei wird eure IP-Adresse an die OpenStreetMap Foundation übertragen.</p>' +
      '<p><button type="button" class="cg-button">Karte laden</button> ' +
      '<a class="cg-link" href="https://www.openstreetmap.org/node/3255611047">Auf OpenStreetMap öffnen</a></p></div>';
    box.querySelector("button").addEventListener("click", function () { zeigen(box); });
  });
})();
