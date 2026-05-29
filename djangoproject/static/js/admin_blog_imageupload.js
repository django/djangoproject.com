document.addEventListener('DOMContentLoaded', () => {
  for (const el of document.querySelectorAll(
    'button[data-clipboard-content]',
  )) {
    el.addEventListener('click', (e) => {
      // Copy to clipboard and flash the button for a second
      navigator.clipboard.writeText(el.dataset.clipboardContent);
      el.style.backgroundColor = 'rebeccapurple';
      el.style.color = 'white';
      globalThis.setTimeout(() => {
        el.style.backgroundColor = '';
        el.style.color = '';
      }, 1000);
    });
  }
});
