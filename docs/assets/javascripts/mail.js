/*
  Hinter jeden E-Mail-Knopf (mailto-Link mit Klasse cg-button) einen Hinweis
  mit der Adresse und "Adresse kopieren" setzen. Hintergrund: mailto öffnet
  nur dann etwas, wenn auf dem Gerät ein Mailprogramm eingerichtet ist. Wer
  im Browser mailt (Outlook im Web, Gmail) oder an einem Firmenrechner ohne
  Mailprogramm sitzt, sieht sonst beim Klick gar nichts.
*/
(function () {
  var EN = (document.documentElement.lang || "").indexOf("en") === 0;
  var T = EN
    ? { oder: "No mail program? Write to", kopieren: "Copy address", kopiert: "Copied" }
    : { oder: "Kein Mailprogramm? Schreibt an", kopieren: "Adresse kopieren", kopiert: "Kopiert" };

  function einbauen() {
    var knoepfe = document.querySelectorAll('a.cg-button[href^="mailto:"]');
    Array.prototype.forEach.call(knoepfe, function (a) {
      if (a.dataset.cgMail) return;
      a.dataset.cgMail = "1";
      var adresse = decodeURIComponent(a.getAttribute("href").slice(7).split("?")[0]);
      var p = document.createElement("p");
      p.className = "cg-mail-hinweis";
      p.appendChild(document.createTextNode(T.oder + " "));
      var code = document.createElement("strong");
      code.textContent = adresse;
      p.appendChild(code);
      if (navigator.clipboard && window.isSecureContext) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "cg-mail-kopieren";
        b.textContent = T.kopieren;
        b.addEventListener("click", function () {
          navigator.clipboard.writeText(adresse).then(function () {
            b.textContent = T.kopiert;
            setTimeout(function () { b.textContent = T.kopieren; }, 2000);
          });
        });
        p.appendChild(document.createTextNode(" "));
        p.appendChild(b);
      }
      var block = a.closest("p") || a;
      block.parentNode.insertBefore(p, block.nextSibling);
    });
  }
  // Zensical lädt Seiten teils ohne Neuladen nach (instant navigation).
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(einbauen);
  else document.addEventListener("DOMContentLoaded", einbauen);
})();
