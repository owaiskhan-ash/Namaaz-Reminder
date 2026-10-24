/* Mobile navigation for the Just Apps pages.

   The header links collapse below 940px (see styles.css). This opens them as a
   sheet, keeps aria-expanded and the button label in sync, locks the page
   behind the sheet, and closes it on link click, outside tap, Escape or a
   resize back to the desktop layout. Without JS the CSS keeps the links hidden
   on small screens, so the page is still usable but a visitor loses the menu;
   that is why the toggle is rendered by the markup, not by this script. */

(function () {
  'use strict';

  var toggle = document.querySelector('[data-nav-toggle]');
  var links = document.getElementById('primary-nav');
  if (!toggle || !links) return;

  var root = document.documentElement;

  function setOpen(open) {
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    links.classList.toggle('is-open', open);
    root.classList.toggle('nav-open', open);
  }

  toggle.addEventListener('click', function () {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true');
  });

  links.addEventListener('click', function (event) {
    if (event.target.closest('a')) setOpen(false);
  });

  /* A tap anywhere outside the sheet closes it. Taps on the theme button are
     left alone so the theme can be changed with the menu still open. */
  document.addEventListener('click', function (event) {
    if (toggle.getAttribute('aria-expanded') !== 'true') return;
    if (toggle.contains(event.target) || links.contains(event.target)) return;
    if (event.target.closest('[data-theme-toggle]')) return;
    setOpen(false);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') setOpen(false);
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 940) setOpen(false);
  });
})();
