/* Mobile navigation for the Just Apps pages.

   The header links collapse below 940px (see styles.css). This opens them as a
   panel, keeps aria-expanded in sync, and closes on link click, Escape or a
   resize back to the desktop layout. Without JS the CSS keeps the links hidden
   on small screens, so the page is still usable but a visitor loses the menu;
   that is why the toggle is rendered by the markup, not by this script. */

(function () {
  'use strict';

  var toggle = document.querySelector('[data-nav-toggle]');
  var links = document.getElementById('primary-nav');
  if (!toggle || !links) return;

  function setOpen(open) {
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    links.classList.toggle('is-open', open);
  }

  toggle.addEventListener('click', function () {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true');
  });

  links.addEventListener('click', function (event) {
    if (event.target.closest('a')) setOpen(false);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') setOpen(false);
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 940) setOpen(false);
  });
})();
