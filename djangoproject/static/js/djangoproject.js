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

// Toggle mobile menu on button click
document.querySelector('.menu-button').addEventListener('click', function () {
  const menu_el = document.querySelector('#top [role="navigation"]');

  this.classList.toggle('active');
  menu_el.classList.toggle('active');
});

// Update search input placeholder text based on the user's operating system
(function () {
  const el = document.querySelector('#id_q');

  if (!el) {
    return;
  }

  const initial_value = el.getAttribute('placeholder');
  const is_mac = navigator.userAgent.indexOf('Mac') !== -1;
  const new_value = `${initial_value} (${is_mac ? '⌘' : 'Ctrl'} + K)`;

  el.setAttribute('placeholder', new_value);
})();

// Focus, select, and scroll to search input when key combination is pressed
window.addEventListener('keydown', function (e) {
  if (!(e.metaKey || e.ctrlKey) || e.key !== 'k') {
    return;
  }

  if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
    return;
  }

  e.preventDefault();

  const el = document.querySelector('#id_q');

  el.select();
  el.focus({ preventScroll: true });
  el.scrollIntoView({ behavior: 'smooth' });
});
