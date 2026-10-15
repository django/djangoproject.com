// To prevent a flash of un-themed content, this script must be loaded in the
// <head> and cannot be marked async, defer, or type=module.
'use strict';

const themes = ['auto', 'light', 'dark'];
const defaultTheme = themes[0];
const dataSetName = 'theme'; // <html data-___> attr for current theme

const cookieName = 'theme';
const cookieMaxAgeMs = 365 * 24 * 60 * 60 * 1000; // 1 year
const cookieDomain = getCookieDomain(window.location.hostname, [
  // Share the cookie between all subdomains (code, docs, www, etc.) in
  // these base domains. More-specific bases must be listed first.
  'preview.djangoproject.com',
  'djangoproject.com',
  'djangoproject.localhost',
  'djangoproject.local',
  // Any other hostname (localhost, 127.0.0.1, pr-123.readthedocs.build, etc.)
  // will use a host-only cookie.
]);
const cookieSecure = window.location.protocol === 'https:';
const cookieSameSite = 'Lax';

const prefersDarkMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
let prefersDark = prefersDarkMediaQuery.matches;

function setTheme(theme) {
  if (themes.indexOf(theme) < 0) {
    console.error(`Invalid theme: '${theme}'. Resetting to '${defaultTheme}'.`);
    theme = defaultTheme;
  }
  document.documentElement.dataset[dataSetName] = theme;
  setThemeCookie(theme);
}

function cycleTheme() {
  // If prefersDark, cycle Auto (dark) -> Light -> Dark;
  // otherwise, cycle Auto (light) -> Dark -> Light.
  const currentThemeIndex = Math.max(
    0,
    themes.indexOf(document.documentElement.dataset[dataSetName]),
  );
  const direction = prefersDark ? 1 : -1;
  const newThemeIndex =
    (currentThemeIndex + direction + themes.length) % themes.length;
  setTheme(themes[newThemeIndex]);
}

function initTheme() {
  // Set theme stored in cookie if there is one, or fallback to auto mode.
  const currentTheme = getThemeCookie() || defaultTheme;
  setTheme(currentTheme);
}

function setupThemeToggle() {
  // Attach event handlers for theme toggle buttons.
  for (const button of document.getElementsByClassName('theme-toggle')) {
    button.addEventListener('click', cycleTheme);
  }
}

function setThemeCookie(theme) {
  const expires = new Date(Date.now() + cookieMaxAgeMs).toUTCString();
  const attributes = [
    `${cookieName}=${encodeURIComponent(theme)}`,
    'Path=/',
    `Expires=${expires}`,
    `SameSite=${cookieSameSite}`,
    cookieDomain ? `Domain=${cookieDomain}` : '',
    cookieSecure ? 'Secure' : '',
  ];
  document.cookie = attributes.filter(Boolean).join('; ');
}

function getThemeCookie() {
  // This must be synchronous to avoid a flash of un-themed content on load,
  // so cannot use the Cookie Store API.
  const cookie = document.cookie
    .split(/;\s*/g)
    .find((cookie) => cookie.startsWith(`${cookieName}=`));
  return cookie ? decodeURIComponent(cookie.slice(cookieName.length + 1)) : '';
}

function getCookieDomain(hostname, baseDomains) {
  hostname = hostname.toLowerCase();
  for (const baseDomain of baseDomains) {
    if (hostname === baseDomain || hostname.endsWith(`.${baseDomain}`)) {
      return baseDomain;
    }
  }
  return '';
}

initTheme();

document.addEventListener('DOMContentLoaded', function () {
  setupThemeToggle();
});

window.addEventListener('pageshow', function (e) {
  if (e.persisted) {
    // Re-initialize from cookie in case theme was changed on another page.
    initTheme();
  }
});

prefersDarkMediaQuery.addEventListener('change', (e) => {
  prefersDark = e.matches;
});
