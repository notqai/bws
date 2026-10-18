/* BWS Engineering Sdn Bhd: site script (no dependencies)
   Mobile menu · header shadow · footer year · scroll reveal · stat counters
   · gallery filter + lightbox · contact form · careers apply links */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Footer year ---- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---- Header shadow on scroll ---- */
  var header = document.querySelector(".site-header");
  if (header) {
    var scrolled = null, ticking = false;
    var update = function () {
      ticking = false;
      var now = window.scrollY > 8;
      if (now !== scrolled) { scrolled = now; header.classList.toggle("is-scrolled", now); }
    };
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }

  /* ---- Mobile menu (full screen, focus-trapped, Esc to close) ---- */
  var toggle = document.querySelector(".nav-toggle");
  var menu = document.getElementById("mobile-menu");
  if (toggle && menu) {
    var closeBtn = menu.querySelector(".nav-close");
    var focusables = function () {
      return Array.prototype.slice.call(menu.querySelectorAll("a[href], button:not([disabled])"));
    };
    var openMenu = function () {
      menu.hidden = false;
      toggle.setAttribute("aria-expanded", "true");
      document.body.classList.add("menu-open");
      closeBtn.focus();
    };
    var closeMenu = function (returnFocus) {
      menu.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
      document.body.classList.remove("menu-open");
      if (returnFocus !== false) toggle.focus();
    };
    toggle.addEventListener("click", openMenu);
    closeBtn.addEventListener("click", closeMenu);
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeMenu(false);
    });
    menu.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { closeMenu(); return; }
      if (e.key !== "Tab") return;
      var f = focusables(), first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    window.matchMedia("(min-width: 80rem)").addEventListener("change", function (mq) {
      if (mq.matches && !menu.hidden) closeMenu(false);
    });
  }

  /* ---- Scroll reveal + counters ---- */
  var revealEls = document.querySelectorAll(".reveal, .reveal-stagger");
  var counters = document.querySelectorAll("[data-count]");

  function runCounter(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var suffix = el.getAttribute("data-suffix") || "";
    if (reduceMotion) { el.textContent = target + suffix; return; }
    var start = null, duration = 1400;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        if (el.hasAttribute("data-count")) runCounter(el);
        else el.classList.add("is-visible");
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
    counters.forEach(function (el) {
      el.textContent = "0" + (el.getAttribute("data-suffix") || "");
      io.observe(el);
    });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---- Gallery filter ---- */
  var filterBar = document.querySelector("[data-filters]");
  var gallery = document.querySelector("[data-gallery]");
  if (filterBar && gallery) {
    var items = Array.prototype.slice.call(gallery.querySelectorAll("li[data-cat]"));
    var status = document.querySelector("[data-gallery-status]");
    filterBar.addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-filter]");
      if (!btn) return;
      var f = btn.getAttribute("data-filter");
      filterBar.querySelectorAll("button[data-filter]").forEach(function (b) {
        b.setAttribute("aria-pressed", String(b === btn));
      });
      var shown = 0;
      items.forEach(function (li) {
        var match = f === "all" || li.getAttribute("data-cat") === f;
        li.hidden = !match;
        if (match) shown++;
      });
      if (status) status.textContent = "Showing " + shown + " " + (shown === 1 ? "photo" : "photos");
    });
  }

  /* ---- Lightbox (native <dialog>: focus handling + Esc built in) ---- */
  var lb = document.getElementById("lightbox");
  if (lb && gallery && typeof lb.showModal === "function") {
    var lbImg = lb.querySelector("img");
    var lbTitle = lb.querySelector("[data-lb-title]");
    var lbCount = lb.querySelector("[data-lb-count]");
    var current = 0;
    var visible = function () {
      return Array.prototype.slice.call(gallery.querySelectorAll("li[data-cat]:not([hidden]) button[data-full]"));
    };
    var show = function (i) {
      var list = visible();
      if (!list.length) return;
      current = (i + list.length) % list.length;
      var btn = list[current];
      var thumb = btn.querySelector("img");
      lb.classList.remove("is-loaded");
      lbImg.onload = function () { lb.classList.add("is-loaded"); };
      lbImg.src = btn.getAttribute("data-full");
      lbImg.alt = thumb ? thumb.alt : "";
      lbTitle.textContent = btn.getAttribute("data-title") || (thumb ? thumb.alt : "");
      lbCount.textContent = (current + 1) + " / " + list.length;
    };
    gallery.addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-full]");
      if (!btn) return;
      show(visible().indexOf(btn));
      lb.showModal();
    });
    lb.querySelector(".lb-prev").addEventListener("click", function () { show(current - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { show(current + 1); });
    lb.querySelector(".lb-close").addEventListener("click", function () { lb.close(); });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); show(current - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); show(current + 1); }
    });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
    lb.addEventListener("close", function () {
      var list = visible();
      if (list[current]) list[current].focus();
    });
  }

  /* ---- Contact form ----
     If the form's action still contains YOUR_FORM_ID it falls back to a
     pre-filled email (mailto:). Once a real Formspree endpoint is set, it
     submits in the background and shows a success / error message. */
  var form = document.querySelector("[data-contact-form]");
  if (form) {
    var statusEl = form.querySelector(".form-status");
    var setStatus = function (state, msg) {
      statusEl.hidden = false;
      statusEl.setAttribute("data-state", state);
      statusEl.textContent = msg;
    };
    var validate = function () {
      var firstBad = null;
      form.querySelectorAll("[required]").forEach(function (input) {
        var err = document.getElementById(input.id + "-error");
        var ok = input.checkValidity();
        input.setAttribute("aria-invalid", String(!ok));
        if (err) err.hidden = ok;
        if (!ok && !firstBad) firstBad = input;
      });
      if (firstBad) firstBad.focus();
      return !firstBad;
    };
    form.setAttribute("novalidate", "");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.querySelector(".hp input").value) return; // spam honeypot
      if (!validate()) { setStatus("err", "Please fill in the highlighted fields."); return; }
      var data = new FormData(form);
      var action = form.getAttribute("action") || "";

      if (action.indexOf("YOUR_FORM_ID") !== -1 || !window.fetch) {
        var to = form.getAttribute("data-mailto") || "bwsesb@gmail.com";
        var subject = "Website enquiry: " + (data.get("service") || "General") + " (" + (data.get("company") || data.get("name")) + ")";
        var body = [
          "Name: " + data.get("name"),
          "Company: " + (data.get("company") || "-"),
          "Email: " + data.get("email"),
          "Phone: " + (data.get("phone") || "-"),
          "Service of interest: " + (data.get("service") || "-"),
          "",
          data.get("message")
        ].join("\n");
        window.location.href = "mailto:" + to + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
        setStatus("ok", "Your email app should open with your message ready to send. If it doesn't, email us directly at " + to + ".");
        return;
      }

      var submitBtn = form.querySelector("[type=submit]");
      submitBtn.disabled = true;
      fetch(action, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.reset();
          setStatus("ok", "Thank you. Your enquiry has been sent and our team will get back to you shortly.");
        })
        .catch(function () {
          setStatus("err", "Sorry, something went wrong. Please email bwsesb@gmail.com or call 085-652743.");
        })
        .finally(function () { submitBtn.disabled = false; });
    });
  }

  /* ---- Careers: build "Apply via email" links from each job title ---- */
  document.querySelectorAll("[data-apply]").forEach(function (a) {
    var position = a.getAttribute("data-apply");
    var subject = "Job Application – " + position;
    a.href = "mailto:bwsesbhr@gmail.com?subject=" + encodeURIComponent(subject);
  });
})();
