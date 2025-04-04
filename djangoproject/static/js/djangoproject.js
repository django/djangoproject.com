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
  const menu_el = document.querySelector('#top nav');

  this.classList.toggle('active');
  menu_el.classList.toggle('active');
});

// Update search input placeholder text based on the user's operating system
(function () {
  const el = document.getElementById('id_q');

  if (!el) {
    return;
  }

  const original_placeholder = el.getAttribute('placeholder');
  const is_mac = navigator.userAgent.indexOf('Mac') !== -1;
  const new_value = `${original_placeholder} (${is_mac ? '⌘\u200aK' : 'Ctrl+K'})`;

  el.setAttribute('placeholder', new_value);
})();

// Focus, select, and scroll to search input when key combination is pressed
window.addEventListener('keydown', function (e) {
  const is_ctrl_k = (e.metaKey || e.ctrlKey) && e.key === 'k';

  if (!(is_ctrl_k || e.key === '/')) {
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

// Add copy buttons to code snippets
(function () {
  const button_el = document.createElement('span');

  button_el.classList.add('btn-clipboard');
  button_el.setAttribute('title', 'Copy this code');
  button_el.innerHTML = '<i class="icon icon-clipboard"></i>';

  const selector = '.snippet-filename, .code-block-caption';

  document.querySelectorAll(selector).forEach(function (el) {
    el.insertBefore(button_el.cloneNode(true), null);
  });
})();

// Attach copy functionality to dynamically-created buttons
document.querySelectorAll('.btn-clipboard').forEach(function (el) {
  el.addEventListener('click', function () {
    const success_el = document.createElement('span');

    success_el.classList.add('clipboard-success');

    this.prepend(success_el);

    success_el.addEventListener('transitionend', function () {
      this.remove();
    });

    function on_success(el) {
      success_el.innerText = 'Copied!';

      setTimeout(function () {
        success_el.classList.add('fade-out');
      }, 1000);
    }

    function on_error(el) {
      success_el.innerText = 'Could not copy!';

      setTimeout(function () {
        success_el.classList.add('fade-out');
      }, 5000);
    }

    const text = this.parentElement.nextElementSibling.textContent.trim();

    navigator.clipboard.writeText(text).then(on_success, on_error);
  });
});

// Compensate for floating warning element when scrolling to a URL hash in docs
(function () {
  const warning_el = document.querySelector('.doc-floating-warning');

  if (!warning_el) {
    return;
  }

  // This element will dynamically enforce the correct amount of top spacing
  const warning_el_copy = warning_el.cloneNode(true);

  warning_el_copy.style.position = 'relative';

  document.body.prepend(warning_el_copy);

  function scroll_to_hash(e) {
    const target_el = document.querySelector(window.location.hash || null);

    if (!target_el) {
      return;
    }

    const y_position = target_el.getBoundingClientRect().top + window.scrollY;
    const correction = -warning_el.offsetHeight - 4;

    window.scrollTo(0, y_position + correction);
  }

  setTimeout(scroll_to_hash, 50);

  window.addEventListener('hashchange', scroll_to_hash);
})();

// Update donate button text on fundraising page based on interval selection
(function () {
  const el = document.querySelector('#donate #id_interval');

  if (!el) {
    return;
  }

  el.addEventListener('change', function () {
    const text = this.value === 'onetime' ? 'Donate' : `Donate ${this.value}`;

    document.getElementById('donate-button').value = text;
  });
})();

// Manage custom donation amount input on fundraising page
(function () {
  const el = document.querySelector('#donate #id_amount');

  if (!el) {
    return;
  }

  el.addEventListener('change', function () {
    if (this.value !== 'custom') {
      return;
    }

    const input_el = document.createElement('input');

    input_el.setAttribute('type', 'number');
    input_el.setAttribute('name', 'amount');

    const custom_donation_el = document.querySelector('.custom-donation');

    custom_donation_el.appendChild(input_el);
    custom_donation_el.style.display = 'block';

    this.remove();

    input_el.focus();
    input_el.value = '25';
  });
})();
