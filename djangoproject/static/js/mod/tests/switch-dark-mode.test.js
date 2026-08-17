import { describe, expect, test } from 'vitest';

import { getCookie, setCookie } from '../switch-dark-mode.js';

describe('getCookie', async () => {
  test('returns the value of a cookie if it exists', async () => {
    document.cookie = 'theme=dark; path=/;';
    expect(getCookie('theme').toString()).toBe('dark');
  });

  test('returns an empty string if the cookie does not exist', async () => {
    document.cookie = 'theme=dark; path=/;';
    expect(getCookie('nonexistent').toString()).toBe('');
  });
});

describe('setCookie', async () => {
  test('name and value', async () => {
    setCookie('testCookie', 'testValue', 'localhost');
    expect(document.cookie).toMatch(/testCookie=testValue/);
  });

  test('SameSite for localhost', async () => {
    setCookie('testCookie', 'testValue', 'localhost');
    expect(document.cookie).not.toMatch(/SameSite=Lax/);
  });
});
