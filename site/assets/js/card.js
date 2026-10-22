/* Digital business card (site/card/*.html): Share button. Uses the system share sheet where there is one,
   otherwise copies the card's link. The button stays hidden without JavaScript. */
(function () {
  var b = document.getElementById('share');
  if (!b) return;
  b.hidden = false;
  b.addEventListener('click', function () {
    var data = { title: document.title, url: location.href };
    if (navigator.share) {
      navigator.share(data).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(data.url).then(function () { b.textContent = 'Link copied'; });
    }
  });
})();
