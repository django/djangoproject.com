// Toggle persistent display of documentation version and language options
document.querySelectorAll('.doc-switcher li.current').forEach(function (el) {
  el.addEventListener('click', function () {
    this.parentElement.classList.toggle('open');
  });
});

// Propagate the current fragment identifier when switching docs versions
document.querySelectorAll('#doc-versions a').forEach(function (el) {
  el.addEventListener('click', function () {
    this.href = this.href.split('#')[0] + window.location.hash;
  });
});

// Fade out and remove message elements when close icon is clicked
document.querySelectorAll('.messages li .close').forEach(function (el) {
  el.addEventListener('click', function (e) {
    this.parentElement.classList.add('fade-out');

    setTimeout(function () {
      el.parentElement.style.display = 'none';
    }, 400);
  });
});
