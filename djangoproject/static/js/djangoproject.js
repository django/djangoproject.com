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
  el.addEventListener('click', function () {
    this.parentElement.addEventListener('transitionend', function () {
      this.style.display = 'none';
    });

    this.parentElement.classList.add('fade-out');
  });
});

// Check all console tab inputs of the same type when one's label is clicked
document.querySelectorAll('.console-block label').forEach(function (el) {
  el.addEventListener('click', function (e) {
    const input_id = e.currentTarget.getAttribute('for');
    const selector = input_id.endsWith('unix') ? '.c-tab-unix' : '.c-tab-win';

    document.querySelectorAll(selector).forEach(function (input_el) {
      input_el.checked = true;
    });
  });
});

// Add animation class to feature icons when they are fully visible
(function () {
  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add('inview');

        observer.unobserve(entry.target);
      });
    },
    { threshold: 1.0 },
  );

  document.querySelectorAll('.list-features i').forEach(function (el) {
    observer.observe(el);
  });
})();
