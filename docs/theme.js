/* Theme switching for the Just Apps pages.
   Dark is the default; light is opt-in and remembered per browser. */

(function () {
  var KEY = 'justapps-theme';
  var root = document.documentElement;

  function read() {
    try {
      var saved = localStorage.getItem(KEY);
      return saved === 'light' || saved === 'dark' ? saved : null;
    } catch (err) {
      return null;
    }
  }

  function paint(theme) {
    root.setAttribute('data-theme', theme);
    root.style.colorScheme = theme;

    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      meta.setAttribute('content', theme === 'dark' ? '#064B4D' : '#F0E3CC');
    }

    var next = theme === 'dark' ? 'light' : 'dark';
    var buttons = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute('aria-pressed', theme === 'light' ? 'true' : 'false');
      buttons[i].setAttribute('aria-label', 'Switch to ' + next + ' mode');
      buttons[i].setAttribute('title', 'Switch to ' + next + ' mode');
    }
  }

  var theme = read() || 'dark';

  /* Set before first paint so the page never flashes the wrong theme. */
  root.setAttribute('data-theme', theme);
  root.style.colorScheme = theme;

  function wire() {
    paint(theme);

    var buttons = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener('click', function () {
        theme = theme === 'dark' ? 'light' : 'dark';
        try {
          localStorage.setItem(KEY, theme);
        } catch (err) {
          /* storage can be blocked; the toggle still works for this page */
        }
        paint(theme);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else {
    wire();
  }
})();
