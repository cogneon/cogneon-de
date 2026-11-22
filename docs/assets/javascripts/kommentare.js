/*
  Kommentare aus dem Fediverse unter Blogbeiträgen.

  Die Kommentare sind die öffentlichen Antworten auf den Toot zum Beitrag. Sie
  werden erst nach Klick auf "Kommentare laden" von der Mastodon-Instanz geholt
  (öffentliche API, ohne Anmeldung) und vor dem Einfügen bereinigt: Es bleiben
  nur Text, Absätze, Zeilenumbrüche und Links. Keine Profilbilder, damit der
  Browser nichts von fremden Servern lädt.

  Idee nach Carl Schwan, "Adding comments to your static blog with Mastodon"
  (https://carlschwan.eu/2020/12/29/adding-comments-to-your-static-blog-with-mastodon/).
*/
(function () {
  "use strict";

  var MAX_TIEFE = 3;

  // Mastodon-HTML -> sicherer DOM-Baum (nur p, br, a mit http(s)-Link, Text).
  function bereinigen(html) {
    var quelle = new DOMParser().parseFromString("<div>" + html + "</div>", "text/html").body.firstChild;
    var ziel = document.createDocumentFragment();
    function kopieren(knoten, in_) {
      knoten.childNodes.forEach(function (k) {
        if (k.nodeType === 3) {
          in_.appendChild(document.createTextNode(k.nodeValue));
        } else if (k.nodeType === 1) {
          var tag = k.tagName.toLowerCase();
          if (tag === "br") {
            in_.appendChild(document.createElement("br"));
          } else if (tag === "p") {
            var p = document.createElement("p");
            kopieren(k, p);
            in_.appendChild(p);
          } else if (tag === "a") {
            var href = k.getAttribute("href") || "";
            if (/^https?:\/\//i.test(href)) {
              var a = document.createElement("a");
              a.href = href;
              a.rel = "nofollow noopener ugc";
              a.textContent = k.textContent;
              in_.appendChild(a);
            } else {
              in_.appendChild(document.createTextNode(k.textContent));
            }
          } else if (tag !== "script" && tag !== "style") {
            kopieren(k, in_); // span u.ä.: nur der Inhalt
          }
        }
      });
    }
    kopieren(quelle, ziel);
    return ziel;
  }

  function datum(iso) {
    try {
      return new Date(iso).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" });
    } catch (e) {
      return "";
    }
  }

  function kommentar(s, tiefe) {
    var el = document.createElement("article");
    el.className = "cg-kommentar";
    el.style.setProperty("--tiefe", String(Math.min(tiefe, MAX_TIEFE)));
    var kopf = document.createElement("p");
    kopf.className = "cg-kommentar__kopf";
    var name = document.createElement("a");
    name.href = /^https?:\/\//i.test(s.account.url) ? s.account.url : "#";
    name.rel = "nofollow noopener ugc";
    name.className = "cg-kommentar__name";
    name.textContent = s.account.display_name || s.account.username;
    var konto = document.createElement("span");
    konto.className = "cg-kommentar__konto";
    konto.textContent = " @" + s.account.acct + " · ";
    var zeit = document.createElement("a");
    zeit.href = /^https?:\/\//i.test(s.url) ? s.url : "#";
    zeit.rel = "nofollow noopener ugc";
    zeit.textContent = datum(s.created_at);
    kopf.append(name, konto, zeit);
    var text = document.createElement("div");
    text.className = "cg-kommentar__text";
    if (s.spoiler_text) {
      var cw = document.createElement("p");
      cw.className = "cg-kommentar__cw";
      cw.textContent = "Inhaltswarnung: " + s.spoiler_text;
      text.appendChild(cw);
    }
    text.appendChild(bereinigen(s.content || ""));
    el.append(kopf, text);
    return el;
  }

  function laden(bereich) {
    var liste = bereich.querySelector(".cg-kommentare__liste");
    var knopf = bereich.querySelector(".cg-kommentare__laden");
    var ausblenden = [];
    try {
      ausblenden = JSON.parse(bereich.dataset.ausblenden || "[]");
    } catch (e) {}
    knopf.disabled = true;
    knopf.textContent = "Wird geladen …";
    var adresse = bereich.dataset.instanz + "/api/v1/statuses/" + encodeURIComponent(bereich.dataset.id) + "/context";
    fetch(adresse, { credentials: "omit", referrerPolicy: "no-referrer" })
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(function (daten) {
        var antworten = (daten.descendants || []).filter(function (s) {
          return (s.visibility === "public" || s.visibility === "unlisted") &&
            ausblenden.indexOf(s.url) < 0 && ausblenden.indexOf(s.uri) < 0;
        });
        // Tiefe im Gesprächsbaum, ausgehend vom Toot zum Beitrag.
        var tiefe = {};
        tiefe[bereich.dataset.id] = 0;
        var sichtbar = {};
        sichtbar[bereich.dataset.id] = true;
        liste.textContent = "";
        var anzahl = 0;
        antworten.forEach(function (s) {
          if (!sichtbar[s.in_reply_to_id]) return; // Antwort auf ausgeblendeten Kommentar
          sichtbar[s.id] = true;
          tiefe[s.id] = (tiefe[s.in_reply_to_id] || 0) + 1;
          liste.appendChild(kommentar(s, tiefe[s.id] - 1));
          anzahl += 1;
        });
        if (!anzahl) {
          var leer = document.createElement("p");
          leer.textContent = "Noch keine Kommentare. Antwortet auf den Beitrag auf Mastodon und macht den Anfang.";
          liste.appendChild(leer);
        }
        knopf.parentNode.remove();
      })
      .catch(function () {
        knopf.disabled = false;
        knopf.textContent = "Erneut versuchen";
        liste.textContent = "Die Kommentare konnten gerade nicht geladen werden.";
      });
  }

  function einrichten() {
    document.querySelectorAll(".cg-kommentare").forEach(function (bereich) {
      var knopf = bereich.querySelector(".cg-kommentare__laden");
      if (!knopf || knopf.dataset.bereit) return;
      knopf.dataset.bereit = "1";
      knopf.addEventListener("click", function () { laden(bereich); });
    });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(einrichten);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", einrichten);
  } else {
    einrichten();
  }
})();
