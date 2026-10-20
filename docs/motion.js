/* Slow, silky interactions for the Just Apps pages.

   1. Inertia scrolling — wheel input is eased into a long glide, so the page
      eases in and coastes to a stop instead of jumping.
   2. A dark dot cursor — a small dark disc with a light halo that follows the
      pointer and opens into a ring over links and buttons.

   Both are opt-in per device: they only run for a precise pointer (mouse or
   trackpad) and only when the visitor has not asked for reduced motion.
   Keyboard, scrollbar dragging and touch scrolling keep working natively. */

(function () {
  'use strict';

  var root = document.documentElement;
  var query = function (q) {
    return window.matchMedia ? window.matchMedia(q).matches : false;
  };

  if (query('(prefers-reduced-motion: reduce)')) return;
  if (!query('(hover: hover) and (pointer: fine)')) return;

  /* ---------------------------------------------------------- inertia ---- */

  var EASE = 0.075;          // lower = slower, longer glide
  var WHEEL_STEP = 0.95;     // wheel distance multiplier
  var SNAP_LIMIT = 0.4;      // px below which we settle

  var target = window.pageYOffset || 0;
  var current = target;
  var lastWritten = target;
  var frame = null;

  function maxScroll() {
    return Math.max(
      0,
      (document.documentElement.scrollHeight || 0) - window.innerHeight
    );
  }

  function clamp(value) {
    return Math.min(maxScroll(), Math.max(0, value));
  }

  function tick() {
    current += (target - current) * EASE;
    if (Math.abs(target - current) < SNAP_LIMIT) current = target;

    lastWritten = current;
    window.scrollTo(0, current);

    frame = current === target ? null : window.requestAnimationFrame(tick);
  }

  function glide() {
    if (frame === null) frame = window.requestAnimationFrame(tick);
  }

  window.addEventListener(
    'wheel',
    function (event) {
      if (event.ctrlKey) return;                       // pinch zoom
      if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;  // horizontal rail

      var delta = event.deltaY;
      if (event.deltaMode === 1) delta *= 18;          // lines
      else if (event.deltaMode === 2) delta *= window.innerHeight;

      if (maxScroll() === 0) return;
      event.preventDefault();

      if (frame === null) {
        current = clamp(window.pageYOffset || 0);
        target = current;
      }
      target = clamp(target + delta * WHEEL_STEP);
      glide();
    },
    { passive: false }
  );

  // Anything that moves the page by itself (keys, scrollbar, find-in-page)
  // takes over from the glide instead of fighting it.
  window.addEventListener(
    'scroll',
    function () {
      var y = window.pageYOffset || 0;
      if (Math.abs(y - lastWritten) < 1.5) return;      // our own write

      if (frame !== null) window.cancelAnimationFrame(frame);
      frame = null;
      current = target = lastWritten = y;
    },
    { passive: true }
  );

  window.addEventListener('resize', function () {
    target = clamp(target);
    if (frame === null) {
      current = lastWritten = clamp(window.pageYOffset || 0);
    }
  });

  // In-page links glide too, over the same easing.
  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[href^="#"]');
    if (!link) return;

    var hash = link.getAttribute('href');
    if (!hash || hash === '#') return;

    var section = document.querySelector(hash);
    if (!section) return;

    event.preventDefault();

    var navHeight = 76;
    var top = section.getBoundingClientRect().top + (window.pageYOffset || 0);

    target = clamp(top - navHeight);
    current = clamp(window.pageYOffset || 0);
    lastWritten = current;
    glide();

    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, '', hash);
    }
  });

  root.classList.add('has-inertia');

  /* ----------------------------------------------------------- cursor ---- */

  var dot = document.createElement('div');
  dot.className = 'cursor-dot';
  dot.setAttribute('aria-hidden', 'true');
  document.body.appendChild(dot);
  root.classList.add('has-custom-cursor');

  var pointerX = window.innerWidth / 2;
  var pointerY = window.innerHeight / 2;
  var dotX = pointerX;
  var dotY = pointerY;
  var cursorFrame = null;

  var HOVERABLE = 'a, button, summary, label, input, select, textarea, [role="button"]';

  function paint() {
    dotX += (pointerX - dotX) * 0.45;
    dotY += (pointerY - dotY) * 0.45;

    if (Math.abs(pointerX - dotX) < 0.08 && Math.abs(pointerY - dotY) < 0.08) {
      dotX = pointerX;
      dotY = pointerY;
    }

    dot.style.transform =
      'translate3d(' + dotX.toFixed(2) + 'px,' + dotY.toFixed(2) + 'px,0) translate(-50%,-50%)';

    cursorFrame =
      dotX === pointerX && dotY === pointerY
        ? null
        : window.requestAnimationFrame(paint);
  }

  function show(visible) {
    dot.classList.toggle('is-visible', visible);
  }

  window.addEventListener(
    'pointermove',
    function (event) {
      if (event.pointerType && event.pointerType !== 'mouse') return;

      pointerX = event.clientX;
      pointerY = event.clientY;

      if (!dot.classList.contains('is-visible')) {
        dotX = pointerX;
        dotY = pointerY;
        show(true);
      }

      if (cursorFrame === null) cursorFrame = window.requestAnimationFrame(paint);
    },
    { passive: true }
  );

  window.addEventListener('blur', function () {
    show(false);
  });

  document.documentElement.addEventListener('mouseleave', function () {
    show(false);
  });

  document.addEventListener(
    'pointerover',
    function (event) {
      if (event.target.closest && event.target.closest(HOVERABLE)) {
        dot.classList.add('is-active');
      }
    },
    { passive: true }
  );

  document.addEventListener(
    'pointerout',
    function (event) {
      if (!event.target.closest || !event.target.closest(HOVERABLE)) return;

      var next = event.relatedTarget;
      if (next && next.closest && next.closest(HOVERABLE)) return;

      dot.classList.remove('is-active');
    },
    { passive: true }
  );

  document.addEventListener(
    'pointerdown',
    function (event) {
      if (event.pointerType && event.pointerType !== 'mouse') return;
      dot.classList.add('is-down');
    },
    { passive: true }
  );

  document.addEventListener(
    'pointerup',
    function () {
      dot.classList.remove('is-down');
    },
    { passive: true }
  );
})();
