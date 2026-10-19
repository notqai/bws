/* BWS Engineering Sdn Bhd: site script (no dependencies)
   Mobile menu · header shadow · footer year · scroll reveal · stat counters
   · gallery filter + lightbox · contact form · careers apply links */
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
     Posts to the form's action (contact.php, or a Formspree endpoint) and reads the
     JSON reply. If no form handler answers (a static host without PHP, or offline),
     it falls back to a pre-filled email (mailto:) so the enquiry is never lost. */
  // Shared by the contact and job application forms: flag each invalid required field, focus the first
  var markField = function (input, ok) {
    var err = document.getElementById(input.id + "-error");
    input.setAttribute("aria-invalid", String(!ok));
    if (err) err.hidden = ok;
  };
  var checkFields = function (f) {
    var firstBad = null;
    f.querySelectorAll("[required]:not(:disabled)").forEach(function (input) {
      var ok = input.checkValidity();
      markField(input, ok);
      if (!ok && !firstBad) firstBad = input;
    });
    if (firstBad) firstBad.focus();
    return !firstBad;
  };
  var statusSetter = function (f) {
    var el = f.querySelector(".form-status");
    return function (state, msg) {
      el.hidden = false;
      el.setAttribute("data-state", state);
      el.textContent = msg;
    };
  };

  var form = document.querySelector("[data-contact-form]");
  if (form) {
    var setStatus = statusSetter(form);
    var validate = function () { return checkFields(form); };
    var sendByEmail = function (data) {
      // No form handler available: let the visitor send it with Gmail, Outlook or their mail app
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
      window.location.href = "mailto:" + to + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      setStatus("ok", T("Your email app should open with your enquiry ready to send. If it does not, please email " + to + " directly.",
                        "Aplikasi e-mel anda akan dibuka dengan pertanyaan yang sedia untuk dihantar. Jika tidak, sila e-mel terus ke " + to + "."));
    };
    var ERRORS = {
      rate: ["You have sent several enquiries in a short time. Please try again later, or call 085-652743.",
             "Anda telah menghantar beberapa pertanyaan dalam masa yang singkat. Sila cuba lagi kemudian, atau hubungi 085-652743."],
      invalid: ["Please fill in the highlighted fields.", "Sila lengkapkan ruangan yang ditandakan."],
      send: ["Sorry, your enquiry could not be sent. Please email bws@bwsengineeringsb.com or call 085-652743.",
             "Maaf, pertanyaan anda tidak dapat dihantar. Sila e-mel bws@bwsengineeringsb.com atau hubungi 085-652743."]
    };
    form.setAttribute("novalidate", "");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.querySelector(".hp input").value) return; // spam honeypot
      if (!validate()) { setStatus("err", T(ERRORS.invalid[0], ERRORS.invalid[1])); return; }
      var data = new FormData(form);
      var action = form.getAttribute("action") || "";
      if (!action || action.indexOf("YOUR_FORM_ID") !== -1 || !window.fetch) { sendByEmail(data); return; }

      var submitBtn = form.querySelector("[type=submit]");
      submitBtn.disabled = true;
      fetch(action, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) {
          return r.json().then(function (j) { return j; }, function () { return null; });
        })
        .then(function (j) {
          if (j && j.ok) {
            form.reset();
            setStatus("ok", T("Thank you. Your enquiry has been sent and our team will get back to you shortly.", "Terima kasih. Pertanyaan anda telah dihantar dan pasukan kami akan menghubungi anda tidak lama lagi."));
          } else if (j && ERRORS[j.error]) {
            setStatus("err", T(ERRORS[j.error][0], ERRORS[j.error][1]));
          } else {
            sendByEmail(data); // no JSON reply: this host has no form handler
          }
        }, function () { sendByEmail(data); })
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

  /* ---- Careers: vacancies and online application, from the BWS Portal (Laravel, portal/) ----
     The section stays hidden unless the portal answers, so the "Send your CV" email
     option keeps working on its own. Vacancy text is inserted with textContent only. */
  var openings = document.querySelector("[data-portal]");
  var applyForm = document.querySelector("[data-apply-form]");
  if (openings && applyForm && window.fetch && window.FormData) {
    var portal = openings.getAttribute("data-portal").replace(/\/$/, "");
    var vacList = openings.querySelector("[data-vacancies]");
    var vacSelect = applyForm.querySelector("#a-vacancy");
    var otherField = applyForm.querySelector("[data-position-other]");
    var otherInput = otherField.querySelector("input");
    var setApplyStatus = statusSetter(applyForm);
    var CV_MAX = 5 * 1024 * 1024;
    var el = function (tag, cls, text) {
      var n = document.createElement(tag);
      if (cls) n.className = cls;
      if (text) n.textContent = text;
      return n;
    };
    var fmtDate = function (iso) {
      return new Date(iso + "T00:00:00").toLocaleDateString(BM ? "ms-MY" : "en-MY", { day: "numeric", month: "long", year: "numeric" });
    };
    var syncPosition = function () {
      var general = !vacSelect.value;
      otherField.hidden = !general;
      otherInput.disabled = !general;
      if (!general) markField(otherInput, true);
    };
    var choose = function (id) {
      vacSelect.value = String(id);
      syncPosition();
      document.getElementById("apply-online").scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth" });
      applyForm.querySelector("#a-name").focus({ preventScroll: true });
    };
    vacSelect.addEventListener("change", syncPosition);

    fetch(portal + "/api/vacancies", { headers: { Accept: "application/json" } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (j) {
        if (!j || !j.ok) return;
        var vs = j.vacancies || [];
        vs.forEach(function (v) {
          var li = el("li", "vacancy");
          li.appendChild(el("h3", "", v.title));
          var meta = [v.location, v.employment_type, v.discipline].filter(Boolean);
          if (v.closes_on) meta.push(T("Closes ", "Tutup ") + fmtDate(v.closes_on));
          li.appendChild(el("p", "vacancy-meta", meta.join(" · ")));
          li.appendChild(el("p", "", v.summary));
          if (v.requirements && v.requirements.length) {
            var ul = el("ul");
            v.requirements.forEach(function (r) { ul.appendChild(el("li", "", r)); });
            li.appendChild(ul);
          }
          var b = el("button", "btn btn--ghost", T("Apply for this position", "Mohon jawatan ini"));
          b.type = "button";
          b.setAttribute("aria-label", T("Apply for ", "Mohon jawatan ") + v.title);
          b.addEventListener("click", function () { choose(v.id); });
          li.appendChild(b);
          vacList.appendChild(li);
          var o = el("option", "", v.title + " (" + v.location + ")");
          o.value = v.id;
          vacSelect.appendChild(o);
        });
        openings.querySelector("[data-no-openings]").hidden = vs.length > 0;
        openings.hidden = false;
        var wanted = new URLSearchParams(location.search).get("vacancy");
        if (wanted && vacSelect.querySelector('option[value="' + parseInt(wanted, 10) + '"]')) vacSelect.value = String(parseInt(wanted, 10));
        syncPosition();
      })
      .catch(function () { /* portal not reachable: keep the email option only */ });

    var APPLY_MSG = {
      ok: ["Thank you. Your application has been received. Our recruitment team will contact you if your profile matches a suitable position.",
           "Terima kasih. Permohonan anda telah diterima. Pasukan pengambilan kami akan menghubungi anda jika profil anda sesuai dengan jawatan yang ada."],
      invalid: ["Please fill in the highlighted fields.", "Sila lengkapkan ruangan yang ditandakan."],
      closed: ["This position has just closed. Please choose another position or send a general application.",
               "Jawatan ini baru sahaja ditutup. Sila pilih jawatan lain atau hantar permohonan umum."],
      rate: ["You have sent several applications in a short time. Please try again later.",
             "Anda telah menghantar beberapa permohonan dalam masa yang singkat. Sila cuba lagi kemudian."],
      fail: ["Sorry, your application could not be sent. Please email your CV to bwsesbhr@gmail.com instead.",
             "Maaf, permohonan anda tidak dapat dihantar. Sila e-mel CV anda ke bwsesbhr@gmail.com."]
    };
    var say = function (key) { setApplyStatus(key === "ok" ? "ok" : "err", T(APPLY_MSG[key][0], APPLY_MSG[key][1])); };

    applyForm.setAttribute("novalidate", "");
    applyForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (applyForm.querySelector(".hp input").value) return; // spam honeypot
      var cv = applyForm.querySelector("#a-cv"), file = cv.files && cv.files[0];
      cv.setCustomValidity(file && (file.size > CV_MAX || !/\.(pdf|docx?)$/i.test(file.name)) ? "bad-file" : "");
      if (!checkFields(applyForm)) { say("invalid"); return; }

      var btn = applyForm.querySelector("[type=submit]");
      btn.disabled = true;
      setApplyStatus("busy", T("Sending your application…", "Menghantar permohonan anda…"));
      fetch(applyForm.getAttribute("action"), { method: "POST", body: new FormData(applyForm), headers: { Accept: "application/json" } })
        .then(function (r) {
          return r.json().then(function (j) { return { status: r.status, j: j }; }, function () { return { status: r.status, j: null }; });
        })
        .then(function (res) {
          var j = res.j || {};
          if (j.ok) {
            applyForm.reset();
            applyForm.querySelectorAll("[aria-invalid]").forEach(function (input) { markField(input, true); });
            syncPosition();
            say("ok");
          } else if (j.errors) {
            // Server-side validation (422): flag the fields it names
            var first = null;
            Object.keys(j.errors).forEach(function (name) {
              var input = applyForm.querySelector('[name="' + name + '"]');
              if (input && input.id) { markField(input, false); if (!first) first = input; }
            });
            if (first) first.focus();
            say("invalid");
          } else if (j.error === "closed" || j.error === "rate") {
            say(j.error);
          } else {
            say("fail");
          }
        }, function () { say("fail"); })
        .finally(function () { btn.disabled = false; });
    });
  }

  /* ---- Careers: build "Apply via email" links from each job title ---- */
  document.querySelectorAll("[data-apply]").forEach(function (a) {
    var position = a.getAttribute("data-apply");
    var subject = "Job Application – " + position;
    a.href = "mailto:bwsesbhr@gmail.com?subject=" + encodeURIComponent(subject);
  });
})();
