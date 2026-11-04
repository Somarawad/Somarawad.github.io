/* Somar Awad · portfolio. Small, dependency-free progressive enhancement.
   Everything on the site works without this file; it adds the theme toggle,
   the before/after drag, lite video embeds, play-in-view and scroll reveals. */
(function () {
  "use strict";
  var doc = document.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- theme toggle (preference kept in localStorage, no cookies) ---- */
  function syncToggle() {
    var t = doc.getAttribute("data-theme");
    var next = t === "dark" ? "light" : "dark";
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.setAttribute("aria-label", "Switch to " + next + " theme");
      b.setAttribute("title", "Switch to " + next + " theme");
    });
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-theme-toggle]");
    if (!b) return;
    var t = doc.getAttribute("data-theme") === "dark" ? "light" : "dark";
    doc.setAttribute("data-theme", t);
    try { localStorage.setItem("theme", t); } catch (err) { /* private mode */ }
    syncToggle();
  });
  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: light)");
    var onChange = function (ev) {
      var saved = null;
      try { saved = localStorage.getItem("theme"); } catch (err) {}
      if (!saved) { doc.setAttribute("data-theme", ev.matches ? "light" : "dark"); syncToggle(); }
    };
    if (mq.addEventListener) mq.addEventListener("change", onChange);
  }

  /* ---- ?slots shows the expected file path on every placeholder ---- */
  if (/[?&]slots\b/.test(location.search)) doc.classList.add("show-slots");

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    syncToggle();

    /* ---- before / after slider ---- */
    document.querySelectorAll("[data-compare]").forEach(function (frame) {
      var box = frame.parentElement;
      var range = frame.querySelector(".compare__range");
      function set(v) {
        v = Math.max(0, Math.min(100, v));
        box.style.setProperty("--pos", v + "%");
        range.value = Math.round(v);
        range.setAttribute("aria-valuetext", Math.round(100 - v) + "% after");
      }
      function fromEvent(e) {
        var r = frame.getBoundingClientRect();
        return ((e.clientX - r.left) / r.width) * 100;
      }
      var dragging = false;
      frame.addEventListener("pointerdown", function (e) {
        if (e.button !== undefined && e.button !== 0) return;
        dragging = true;
        if (e.pointerType === "mouse") e.preventDefault();
        range.focus({ preventScroll: true });
        try { frame.setPointerCapture(e.pointerId); } catch (err) {}
        set(fromEvent(e));
      });
      frame.addEventListener("pointermove", function (e) { if (dragging) set(fromEvent(e)); });
      frame.addEventListener("dragstart", function (e) { e.preventDefault(); });
      ["pointerup", "pointercancel", "lostpointercapture"].forEach(function (n) {
        frame.addEventListener(n, function () { dragging = false; });
      });
      range.addEventListener("input", function () { set(Number(range.value)); });
    });

    /* ---- lite embeds: thumbnail until click, then the player ---- */
    document.querySelectorAll(".embed").forEach(function (el) {
      var btn = el.querySelector(".embed__btn");
      if (!btn) return;
      btn.addEventListener("click", function () {
        var f = document.createElement("iframe");
        f.src = el.getAttribute("data-embed");
        f.title = el.getAttribute("data-title") || "Video";
        f.allow = "autoplay; fullscreen; picture-in-picture; encrypted-media";
        f.allowFullscreen = true;
        f.referrerPolicy = "strict-origin-when-cross-origin";
        el.innerHTML = "";
        el.appendChild(f);
        f.focus();
      });
    });

    /* ---- videos: play muted loops only while in view; respect reduced motion ---- */
    var loops = Array.prototype.slice.call(document.querySelectorAll("video[data-inview]"));
    if (reduceMotion) {
      loops.forEach(function (v) { v.removeAttribute("autoplay"); v.pause(); v.controls = true; });
    } else if ("IntersectionObserver" in window) {
      var vio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          var v = en.target;
          if (en.isIntersecting) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
          else v.pause();
        });
      }, { threshold: 0.35 });
      loops.forEach(function (v) { vio.observe(v); });
    }

    /* ---- card hover previews (desktop pointers only) ---- */
    if (!reduceMotion && window.matchMedia("(hover: hover)").matches) {
      document.querySelectorAll(".card__link").forEach(function (a) {
        var v = a.querySelector("video[data-hover]");
        if (!v) return;
        a.addEventListener("mouseenter", function () { var p = v.play(); if (p && p.catch) p.catch(function () {}); });
        a.addEventListener("mouseleave", function () { v.pause(); });
        a.addEventListener("focus", function () { var p = v.play(); if (p && p.catch) p.catch(function () {}); });
        a.addEventListener("blur", function () { v.pause(); });
      });
    }

    /* ---- copy email ---- */
    document.querySelectorAll("[data-copy]").forEach(function (b) {
      b.addEventListener("click", function () {
        var text = b.getAttribute("data-copy");
        var status = b.parentElement.querySelector(".copy-status");
        function done(msg) { if (status) { status.textContent = msg; setTimeout(function () { status.textContent = ""; }, 2500); } }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () { done("Copied"); }, function () { done("Press Ctrl+C to copy"); });
        } else { done("Copy: " + text); }
      });
    });

    /* ---- scroll reveal ---- */
    var reveals = document.querySelectorAll("[data-reveal]");
    if (reduceMotion || !("IntersectionObserver" in window)) {
      reveals.forEach(function (el) { el.classList.add("is-in"); });
    } else {
      var rio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add("is-in"); rio.unobserve(en.target); }
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
      reveals.forEach(function (el) { rio.observe(el); });
    }
  });
})();
