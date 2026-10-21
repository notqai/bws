/* BWS Engineering Sdn Bhd: site script (no dependencies)
   Mobile menu · header shadow · footer year · scroll reveal · stat counters
   · gallery filter + lightbox · contact form · map loader · careers apply links */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var BM = (doc.getAttribute("lang") || "").indexOf("ms") === 0;
  var T = function (en, ms) { return BM ? ms : en; };

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
      if (status) status.textContent = T("Showing " + shown + " " + (shown === 1 ? "photo" : "photos"), "Memaparkan " + shown + " foto");
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
      if (!validate()) { setStatus("err", T("Please fill in the highlighted fields.", "Sila lengkapkan ruangan yang ditandakan.")); return; }
      var data = new FormData(form);
      var action = form.getAttribute("action") || "";

      if (action.indexOf("YOUR_FORM_ID") !== -1 || !window.fetch) {
        // No form service connected: let the visitor send it with Gmail, Outlook or their mail app
        var to = form.getAttribute("data-mailto") || "bws@bwsengineeringsb.com";
        var subject = T("Website enquiry: ", "Pertanyaan laman web: ") + (data.get("service") || T("General", "Umum")) + " (" + (data.get("company") || data.get("name")) + ")";
        var body = [
          T("Name: ", "Nama: ") + data.get("name"),
          T("Company: ", "Syarikat: ") + (data.get("company") || "-"),
          T("Email: ", "E-mel: ") + data.get("email"),
          T("Phone: ", "Telefon: ") + (data.get("phone") || "-"),
          T("Service of interest: ", "Perkhidmatan: ") + (data.get("service") || "-"),
          "",
          data.get("message")
        ].join("\n");
        var enc = encodeURIComponent;
        var links = [
          ["Gmail", "https://mail.google.com/mail/?view=cm&fs=1&to=" + enc(to) + "&su=" + enc(subject) + "&body=" + enc(body), true],
          ["Outlook", "https://outlook.office.com/mail/deeplink/compose?to=" + enc(to) + "&subject=" + enc(subject) + "&body=" + enc(body), true],
          [T("Email app", "Aplikasi e-mel"), "mailto:" + to + "?subject=" + enc(subject) + "&body=" + enc(body), false]
        ];
        statusEl.hidden = false;
        statusEl.setAttribute("data-state", "ok");
        statusEl.textContent = "";
        var p = document.createElement("p");
        p.textContent = T("Your message is ready. Choose how to send it to " + to + ":", "Mesej anda sudah sedia. Pilih cara menghantarnya ke " + to + ":");
        var group = document.createElement("div");
        group.className = "mail-choice";
        links.forEach(function (l, i) {
          var a = document.createElement("a");
          a.className = i === 0 ? "btn btn--primary" : "btn btn--ghost";
          a.href = l[1];
          a.textContent = l[0];
          if (l[2]) { a.target = "_blank"; a.rel = "noopener"; }
          group.appendChild(a);
        });
        statusEl.appendChild(p);
        statusEl.appendChild(group);
        group.querySelector("a").focus();
        return;
      }

      var submitBtn = form.querySelector("[type=submit]");
      submitBtn.disabled = true;
      fetch(action, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.reset();
          setStatus("ok", T("Thank you. Your enquiry has been sent and our team will get back to you shortly.", "Terima kasih. Pertanyaan anda telah dihantar dan pasukan kami akan menghubungi anda tidak lama lagi."));
        })
        .catch(function () {
          setStatus("err", T("Sorry, something went wrong. Please email bws@bwsengineeringsb.com or call 085-652743.", "Maaf, berlaku ralat. Sila e-mel bws@bwsengineeringsb.com atau hubungi 085-652743."));
        })
        .finally(function () { submitBtn.disabled = false; });
    });
  }

  /* ---- Full project list: search + sector filter ---- */
  var flBody = document.querySelector("[data-fl-body]");
  if (flBody) {
    var flRows = Array.prototype.slice.call(flBody.querySelectorAll("tr"));
    var flSearch = document.querySelector("[data-fl-search]");
    var flFilters = document.querySelector("[data-fl-filters]");
    var flStatus = document.querySelector("[data-fl-status]");
    var sector = "all";
    var apply = function () {
      var q = (flSearch.value || "").toLowerCase().trim(), shown = 0;
      flRows.forEach(function (tr) {
        var ok = (sector === "all" || tr.getAttribute("data-sector") === sector) && (!q || tr.textContent.toLowerCase().indexOf(q) !== -1);
        tr.hidden = !ok; if (ok) shown++;
      });
      if (flStatus) flStatus.textContent = T(shown + " projects shown", shown + " projek dipaparkan");
    };
    flSearch.addEventListener("input", apply);
    flFilters.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-fl]"); if (!b) return;
      sector = b.getAttribute("data-fl");
      flFilters.querySelectorAll("button[data-fl]").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      apply();
    });
  }

  /* ---- Contact: pre-select the service when arriving from a Services page (contact.html?service=civil) ---- */
  var svcKey = new URLSearchParams(location.search).get("service");
  if (svcKey) {
    var opt = document.querySelector('#f-service option[data-key="' + svcKey + '"]');
    if (opt) opt.selected = true;
  }

  /* ---- Careers: build "Apply via email" links from each job title ---- */
  document.querySelectorAll("[data-apply]").forEach(function (a) {
    var position = a.getAttribute("data-apply");
    var subject = "Job Application – " + position;
    a.href = "mailto:bwsesbhr@gmail.com?subject=" + encodeURIComponent(subject);
  });

  /* ---- Contact: the site drawings swap in the Google map only when asked ---- */
  document.querySelectorAll(".map-wrap[data-map-src]").forEach(function (wrap) {
    var load = wrap.querySelector(".map-load");
    if (!load) return;
    load.addEventListener("click", function () {
      var frame = document.createElement("iframe");
      frame.className = "map";
      frame.src = wrap.getAttribute("data-map-src");
      frame.title = wrap.getAttribute("data-map-title");
      frame.setAttribute("referrerpolicy", "no-referrer-when-downgrade");
      wrap.replaceChildren(frame);
      frame.focus();
    });
  });
})();
