/* Tactile, silky interactions for the Just Apps pages.

   1. Active section indicator (#7) — highlights current nav link on scroll.
   2. Smooth FAQ unfold (#5) — eases <details> height open and closed.
   3. Gentle depth parallax (#2) — subtle differential motion between hides.
   4. Soft studio light follow (#4) — subtle grazing sheen across cards.
   5. Inertia scrolling & precision cursor — opt-in for fine pointers.

   Respects prefers-reduced-motion and degrades gracefully without JS. */

(function () {
  'use strict';

  var root = document.documentElement;
  var query = function (q) {
    return window.matchMedia ? window.matchMedia(q).matches : false;
  };

  var reducedMotion = query('(prefers-reduced-motion: reduce)');
  var finePointer = query('(hover: hover) and (pointer: fine)');

  /* --------------------------------------- #7 active nav tab indicator -- */

  var navLinks = Array.prototype.slice.call(
    document.querySelectorAll('.nav-links a[href^="#"]:not(.nav-cta)')
  );
  var trackedSections = [];
  for (var i = 0; i < navLinks.length; i++) {
    var href = navLinks[i].getAttribute('href');
    var sec = href && href.length > 1 ? document.querySelector(href) : null;
    if (sec) trackedSections.push({ link: navLinks[i], section: sec });
  }

  function updateActiveNav() {
    if (!trackedSections.length) return;
    var scrollPos = (window.pageYOffset || 0) + window.innerHeight * 0.28;
    var active = null;

    for (var j = 0; j < trackedSections.length; j++) {
      var rect = trackedSections[j].section.getBoundingClientRect();
      var top = rect.top + (window.pageYOffset || 0);
      if (scrollPos >= top) {
        active = trackedSections[j].link;
      }
    }

    for (var k = 0; k < trackedSections.length; k++) {
      var lnk = trackedSections[k].link;
      var isCurrent = lnk === active;
      lnk.classList.toggle('is-current', isCurrent);
      if (isCurrent) {
        lnk.setAttribute('aria-current', 'true');
      } else {
        lnk.removeAttribute('aria-current');
      }
    }
  }

  /* ------------------------------------- #2 gentle leather parallax ----- */

  var stages = Array.prototype.slice.call(
    document.querySelectorAll('.leather-stage')
  );

  function updateParallax() {
    if (reducedMotion || !stages.length) return;
    var y = window.pageYOffset || 0;
    var vh = window.innerHeight || 900;

    for (var s = 0; s < stages.length; s++) {
      var el = stages[s];
      var r = el.getBoundingClientRect();
      if (r.bottom < -120 || r.top > vh + 120) continue;

      var progress;
      if (el.classList.contains('leather-stage-top')) {
        // Anchored at 0 on initial paint, gently separates as you scroll down
        progress = Math.min(1.2, Math.max(0, y / Math.max(480, vh)));
      } else {
        var centerOffset = (vh * 0.5 - (r.top + r.height * 0.5)) / vh;
        progress = Math.min(1.2, Math.max(-1.2, centerOffset));
      }

      el.style.setProperty('--py-base', (progress * 3.5).toFixed(2) + 'px');
      el.style.setProperty('--py-under', (progress * 6.5).toFixed(2) + 'px');
      el.style.setProperty('--py-over', (progress * -9.5).toFixed(2) + 'px');
    }
  }

  var scrollTicking = false;
  function onScrollScene() {
    if (scrollTicking) return;
    scrollTicking = true;
    window.requestAnimationFrame(function () {
      scrollTicking = false;
      updateActiveNav();
      updateParallax();
    });
  }

  window.addEventListener('scroll', onScrollScene, { passive: true });
  window.addEventListener('resize', onScrollScene, { passive: true });
  updateActiveNav();
  updateParallax();

  if (reducedMotion) return;

  /* ------------------------------- #5 smooth FAQ accordion unfold ------- */

  var accordions = document.querySelectorAll('.faq-list details');
  Array.prototype.forEach.call(accordions, function (details) {
    var summary = details.querySelector('summary');
    if (!summary || !details.animate) return;
    var anim = null;

    summary.addEventListener('click', function (event) {
      event.preventDefault();
      if (anim) anim.cancel();

      var startHeight = details.offsetHeight;

      if (details.open) {
        var closedHeight = summary.offsetHeight;
        anim = details.animate(
          [{ height: startHeight + 'px' }, { height: closedHeight + 'px' }],
          { duration: 240, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' }
        );
        anim.onfinish = function () {
          details.open = false;
          details.style.height = '';
          anim = null;
        };
        anim.oncancel = function () {
          details.style.height = '';
          anim = null;
        };
      } else {
        details.style.height = startHeight + 'px';
        details.open = true;
        var fullHeight = details.scrollHeight;
        anim = details.animate(
          [{ height: startHeight + 'px' }, { height: fullHeight + 'px' }],
          { duration: 270, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' }
        );
        anim.onfinish = function () {
          details.style.height = '';
          anim = null;
        };
        anim.oncancel = function () {
          details.style.height = '';
          anim = null;
        };
      }
    });
  });

  if (!finePointer) return;

  /* ----------------------------- #4 soft studio light follow on cards --- */

  var cards = document.querySelectorAll('.app-card, .feature');
  Array.prototype.forEach.call(cards, function (card) {
    card.addEventListener(
      'pointermove',
      function (event) {
        if (event.pointerType && event.pointerType !== 'mouse') return;
        var rect = card.getBoundingClientRect();
        card.style.setProperty('--mx', (event.clientX - rect.left).toFixed(1) + 'px');
        card.style.setProperty('--my', (event.clientY - rect.top).toFixed(1) + 'px');
        card.style.setProperty('--sheen', '1');
      },
      { passive: true }
    );
    card.addEventListener(
      'pointerleave',
      function () {
        card.style.setProperty('--sheen', '0');
      },
      { passive: true }
    );
  });

  /* ---------------------------------------------------------- inertia ---- */

  var EASE = 0.075;
  var WHEEL_STEP = 0.95;
  var SNAP_LIMIT = 0.4;

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
    updateActiveNav();
    updateParallax();

    frame = current === target ? null : window.requestAnimationFrame(tick);
  }

  function glide() {
    if (frame === null) frame = window.requestAnimationFrame(tick);
  }

  window.addEventListener(
    'wheel',
    function (event) {
      if (event.ctrlKey) return;
      if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;

      var delta = event.deltaY;
      if (event.deltaMode === 1) delta *= 18;
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

  window.addEventListener(
    'scroll',
    function () {
      var y = window.pageYOffset || 0;
      if (Math.abs(y - lastWritten) < 1.5) return;

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
