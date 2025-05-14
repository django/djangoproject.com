document.addEventListener('DOMContentLoaded', function () {
  document
    .querySelectorAll('button[data-clipboard-content]')
    .forEach(function (el) {
      el.addEventListener('click', function (e) {
        // Copy to clipboard and flash the button for a second
        navigator.clipboard.writeText(el.dataset.clipboardContent);
        el.style.backgroundColor = 'rebeccapurple';
        el.style.color = 'white';
        window.setTimeout(function () {
          el.style.backgroundColor = '';
          el.style.color = '';
        }, 1000);
      });
    });
});
