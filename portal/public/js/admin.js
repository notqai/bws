// Ask before destructive actions (forms marked data-confirm)
document.querySelectorAll("form[data-confirm]").forEach(function (f) {
  f.addEventListener("submit", function (e) {
    if (!window.confirm(f.getAttribute("data-confirm"))) e.preventDefault();
  });
});
