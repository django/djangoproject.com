let prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

function setTheme(mode) {
  if (mode !== 'light' && mode !== 'dark' && mode !== 'auto') {
    console.error(`Got invalid theme mode: ${mode}. Resetting to auto.`);
    mode = 'auto';
  }
  document.documentElement.dataset.theme = mode;

  // Determine the cookie domain. We share the cookie across subdomains for known base domains.
  const hostname = window.location.hostname;
  let cookieDomain = '';
  const sharedDomains = ['djangoproject.com', 'djangoproject.local'];
  for (const domain of sharedDomains) {
    if (hostname === domain || hostname.endsWith('.' + domain)) {
      cookieDomain = domain;
      break;
    }
  }

  setCookie('theme', mode, cookieDomain);
}

function cycleTheme() {
  const currentTheme = document.documentElement.dataset.theme || 'auto';

  if (prefersDark) {
    // Auto (dark) -> Light -> Dark
    if (currentTheme === 'auto') {
      setTheme('light');
    } else if (currentTheme === 'light') {
      setTheme('dark');
    } else {
      setTheme('auto');
    }
  } else {
    // Auto (light) -> Dark -> Light
    if (currentTheme === 'auto') {
      setTheme('dark');
    } else if (currentTheme === 'dark') {
      setTheme('light');
    } else {
      setTheme('auto');
    }
  }
}

function initTheme() {
  // set theme defined in cookie if there is one, or fallback to auto mode
  const currentTheme = getCookie('theme');
  currentTheme ? setTheme(currentTheme) : setTheme('auto');
}

function setupTheme() {
  // Attach event handlers for toggling themes
  const buttons = document.getElementsByClassName('theme-toggle');
  for (let i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener('click', cycleTheme);
  }
}

function setCookie(cname, cvalue, domain) {
  const d = new Date();
  d.setTime(d.getTime() + 365 * 24 * 60 * 60 * 1000); // 1 year
  const expires = 'expires=' + d.toUTCString();

  // Determine SameSite and Secure attributes based on protocol
  let sameSiteAttribute = 'SameSite=Lax;';
  if (window.location.protocol === 'https:') {
    sameSiteAttribute = 'SameSite=None; Secure;';
  }

  if (domain) {
    sameSiteAttribute = `Domain=${domain}; ` + sameSiteAttribute;
  }

  document.cookie = `${cname}=${cvalue}; ${sameSiteAttribute} ${expires}; path=/;`;
}

function getCookie(cname) {
  const name = cname + '=';
  const decodedCookie = decodeURIComponent(document.cookie);
  const ca = decodedCookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return '';
}

initTheme();

document.addEventListener('DOMContentLoaded', function () {
  setupTheme();
});

// Update prefersDark if OS preferences change, but do not override manually set theme
window
  .matchMedia('(prefers-color-scheme: dark)')
  .addEventListener('change', function (e) {
    prefersDark = e.matches;
  });

// Reload theme from cookie when loaded from the backward/forward cache (bfcache)
window.addEventListener('pageshow', function (e) {
  if (e.persisted) {
    initTheme();
  }
});
