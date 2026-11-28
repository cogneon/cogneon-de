/*
  Kommentare unter Blogbeiträgen: öffentliche Antworten auf unsere Posts zum
  Beitrag auf Mastodon und Bluesky, zu einem Gespräch zusammengeführt.

  Geladen wird erst nach Klick auf "Kommentare laden", ohne Anmeldung, ohne
  Cookies. Erste Antworten beider Netzwerke stehen nach Zeit sortiert
  untereinander, Antworten darauf eingerückt darunter. Jede Antwort zeigt,
  woher sie kommt, und verlinkt auf das Original. Text wird bereinigt bzw.
  (Bluesky) aus reinem Text aufgebaut: nur Absätze, Zeilenumbrüche und
  http(s)-Links. Keine Profilbilder.

  Idee nach Carl Schwan ("Adding comments to your static blog with Mastodon",
  https://carlschwan.eu/2020/12/29/adding-comments-to-your-static-blog-with-mastodon/)
  und Dirk Primbs (Mastodon und Bluesky in einem Verlauf).
*/
(function () {
  "use strict";

  var MAX_TIEFE = 3;
  var BSKY = "https://public.api.bsky.app/xrpc/";

  function sicherLink(href, text) {
    if (!/^https?:\/\//i.test(href || "")) return document.createTextNode(text);
    var a = document.createElement("a");
    a.href = href;
    a.rel = "nofollow noopener ugc";
    a.textContent = text;
    return a;
  }

  // Mastodon-HTML -> sicherer DOM-Baum (nur p, br, a mit http(s)-Link, Text).
  function mastodonText(html) {
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
            in_.appendChild(sicherLink(k.getAttribute("href"), k.textContent));
          } else if (tag !== "script" && tag !== "style") {
            kopieren(k, in_);
          }
        }
      });
    }
    kopieren(quelle, ziel);
    return ziel;
  }

  // Bluesky: reiner Text + Facetten (Byte-Bereiche) -> Absatz mit Links.
  function blueskyText(text, facetten) {
    var p = document.createElement("p");
    var bytes = new TextEncoder().encode(text || "");
    var dec = new TextDecoder();
    var links = (facetten || []).map(function (f) {
      var feat = (f.features || [])[0] || {};
      var href = feat.uri || (feat.did ? "https://bsky.app/profile/" + feat.did : "");
      return { start: f.index.byteStart, ende: f.index.byteEnd, href: href };
    }).filter(function (l) { return l.href; }).sort(function (a, b) { return a.start - b.start; });
    function textMitUmbruch(stueck) {
      stueck.split("\n").forEach(function (zeile, i) {
        if (i) p.appendChild(document.createElement("br"));
        if (zeile) p.appendChild(document.createTextNode(zeile));
      });
    }
    var pos = 0;
    links.forEach(function (l) {
      if (l.start < pos) return;
      textMitUmbruch(dec.decode(bytes.slice(pos, l.start)));
      p.appendChild(sicherLink(l.href, dec.decode(bytes.slice(l.start, l.ende))));
      pos = l.ende;
    });
    textMitUmbruch(dec.decode(bytes.slice(pos)));
    return p;
  }

  function datum(iso) {
    try {
      return new Date(iso).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" });
    } catch (e) {
      return "";
    }
  }

  // ---- Laden je Netzwerk: Liste einheitlicher Kommentare {id, eltern, zeit, ...}

  function mastodonLaden(bereich, ausblenden) {
    var instanz = bereich.dataset.instanz, wurzel = bereich.dataset.id;
    if (!instanz || !wurzel) return Promise.resolve([]);
    return fetch(instanz + "/api/v1/statuses/" + encodeURIComponent(wurzel) + "/context",
                 { credentials: "omit", referrerPolicy: "no-referrer" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (daten) {
        var sichtbar = {};
        sichtbar[wurzel] = true;
        var liste = [];
        (daten.descendants || []).forEach(function (s) {
          var oeffentlich = s.visibility === "public" || s.visibility === "unlisted";
          var versteckt = ausblenden.indexOf(s.url) >= 0 || ausblenden.indexOf(s.uri) >= 0;
          if (!oeffentlich || versteckt || !sichtbar[s.in_reply_to_id]) return;
          sichtbar[s.id] = true;
          liste.push({
            id: "m:" + s.id, eltern: s.in_reply_to_id === wurzel ? null : "m:" + s.in_reply_to_id,
            zeit: s.created_at, netz: "Mastodon",
            name: s.account.display_name || s.account.username, konto: "@" + s.account.acct,
            profil: s.account.url, url: s.url, cw: s.spoiler_text, inhalt: mastodonText(s.content || "")
          });
        });
        return liste;
      });
  }

  function blueskyLaden(bereich, ausblenden) {
    var autor = bereich.dataset.bskyAutor, rkey = bereich.dataset.bskyRkey;
    if (!autor || !rkey) return Promise.resolve([]);
    var didHolen = /^did:/.test(autor) ? Promise.resolve(autor) :
      fetch(BSKY + "com.atproto.identity.resolveHandle?handle=" + encodeURIComponent(autor), { credentials: "omit" })
        .then(function (r) { return r.json(); }).then(function (d) { return d.did; });
    return didHolen.then(function (did) {
      var uri = "at://" + did + "/app.bsky.feed.post/" + rkey;
      return fetch(BSKY + "app.bsky.feed.getPostThread?depth=10&parentHeight=0&uri=" + encodeURIComponent(uri),
                   { credentials: "omit", referrerPolicy: "no-referrer" });
    }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (daten) {
        var liste = [];
        function versteckt(post, web) {
          var k = post.uri.split("/").pop();
          return ausblenden.some(function (a) {
            return a === post.uri || a === web ||
              (a.indexOf("/post/" + k) > 0 && (a.indexOf(post.author.did) >= 0 || a.indexOf(post.author.handle) >= 0));
          });
        }
        function durchlaufen(knoten, eltern) {
          (knoten.replies || []).forEach(function (antwort) {
            var post = antwort.post;
            if (!post || !post.record) return; // gelöscht oder blockiert
            var web = "https://bsky.app/profile/" + post.author.handle + "/post/" + post.uri.split("/").pop();
            if (versteckt(post, web)) return; // samt Antworten darauf
            var id = "b:" + post.uri;
            liste.push({
              id: id, eltern: eltern, zeit: post.record.createdAt || post.indexedAt, netz: "Bluesky",
              name: post.author.displayName || post.author.handle, konto: "@" + post.author.handle,
              profil: "https://bsky.app/profile/" + post.author.handle, url: web,
              inhalt: blueskyText(post.record.text, post.record.facets)
            });
            durchlaufen(antwort, id);
          });
        }
        durchlaufen(daten.thread || {}, null);
        return liste;
      });
  }

  // ---- Anzeige

  function kommentar(k, tiefe) {
    var el = document.createElement("article");
    el.className = "cg-kommentar";
    el.style.setProperty("--tiefe", String(Math.min(tiefe, MAX_TIEFE)));
    var kopf = document.createElement("p");
    kopf.className = "cg-kommentar__kopf";
    var name = sicherLink(k.profil, k.name);
    if (name.classList) name.classList.add("cg-kommentar__name");
    var konto = document.createElement("span");
    konto.className = "cg-kommentar__konto";
    konto.textContent = " " + k.konto + " · ";
    var netz = document.createElement("span");
    netz.className = "cg-kommentar__netz cg-kommentar__netz--" + k.netz.toLowerCase();
    netz.textContent = k.netz;
    kopf.append(name, konto, sicherLink(k.url, datum(k.zeit)), document.createTextNode(" · "), netz);
    var text = document.createElement("div");
    text.className = "cg-kommentar__text";
    if (k.cw) {
      var cw = document.createElement("p");
      cw.className = "cg-kommentar__cw";
      cw.textContent = "Inhaltswarnung: " + k.cw;
      text.appendChild(cw);
    }
    text.appendChild(k.inhalt);
    el.append(kopf, text);
    return el;
  }

  function anzeigen(liste, alle) {
    var kinder = {}, nachZeit = function (a, b) { return new Date(a.zeit) - new Date(b.zeit); };
    alle.forEach(function (k) { (kinder[k.eltern || ""] = kinder[k.eltern || ""] || []).push(k); });
    function ausgeben(eltern, tiefe) {
      (kinder[eltern] || []).sort(nachZeit).forEach(function (k) {
        liste.appendChild(kommentar(k, tiefe));
        ausgeben(k.id, tiefe + 1);
      });
    }
    ausgeben("", 0);
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
    var fehler = [];
    function sammeln(name, versprechen) {
      return versprechen.catch(function () { fehler.push(name); return []; });
    }
    Promise.all([sammeln("Mastodon", mastodonLaden(bereich, ausblenden)),
                 sammeln("Bluesky", blueskyLaden(bereich, ausblenden))])
      .then(function (ergebnisse) {
        var alle = ergebnisse[0].concat(ergebnisse[1]);
        liste.textContent = "";
        anzeigen(liste, alle);
        if (!alle.length && !fehler.length) {
          var leer = document.createElement("p");
          leer.textContent = "Noch keine Kommentare. Antwortet auf unseren Beitrag und macht den Anfang.";
          liste.appendChild(leer);
        }
        if (fehler.length) {
          var hinweis = document.createElement("p");
          hinweis.className = "cg-muted";
          hinweis.textContent = "Antworten von " + fehler.join(" und ") + " konnten gerade nicht geladen werden.";
          liste.appendChild(hinweis);
        }
        if (fehler.length === 2) {
          knopf.disabled = false;
          knopf.textContent = "Erneut versuchen";
        } else {
          knopf.parentNode.remove();
        }
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
