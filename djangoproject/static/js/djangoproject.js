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
  el.focus();

  window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
});

// Add copy buttons to code snippets and console tabs
(function () {
  const button_el = document.createElement('span');

  button_el.classList.add('btn-clipboard');
  button_el.setAttribute('title', 'Copy this code');
  button_el.innerHTML = '<i class="icon icon-clipboard"></i>';

  document
    .querySelectorAll('.snippet-filename, .code-block-caption')
    .forEach(function (el) {
      el.insertBefore(button_el.cloneNode(true), null);
    });

  document.querySelectorAll('.console-block > section').forEach(function (el) {
    const highlight_el = el.querySelector('.highlight');

    if (highlight_el) {
      highlight_el.appendChild(button_el.cloneNode(true));
    }
  });
})();

// Attach copy functionality to clipboard buttons
document.querySelectorAll('.btn-clipboard').forEach(function (el) {
  el.addEventListener('click', function () {
    const existing_el = this.querySelector('.clipboard-success');

    if (existing_el) {
      existing_el.remove();
    }

    const success_el = document.createElement('span');

    success_el.classList.add('clipboard-success');

    this.prepend(success_el);

    success_el.addEventListener('transitionend', function () {
      this.remove();
    });

    function on_success() {
      success_el.innerText = 'Copied!';

      setTimeout(function () {
        success_el.classList.add('fade-out');
      }, 1000);
    }

    function on_error() {
      success_el.innerText = 'Could not copy!';

      setTimeout(function () {
        success_el.classList.add('fade-out');
      }, 5000);
    }

    let text;
    const console_section = this.closest('.console-block > section');
    const prompt_regex = /^\$ |^\.\.\.\\>/gm;

    if (console_section) {
      const pre_el = console_section.querySelector('.highlight pre');
      text = pre_el.textContent.replace(prompt_regex, '');
    } else {
      text = this.parentElement.nextElementSibling.textContent;
    }

    navigator.clipboard.writeText(text.trim()).then(on_success, on_error);
  });
});

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

// Manage amount and membership level fields on corporate membership page
(function () {
  const form_el = document.querySelector('.corporate-membership-join-form');

  if (!form_el) {
    return;
  }

  const amount_el = form_el.querySelector('#id_amount');
  const level_el = form_el.querySelector('#id_membership_level');
  const levels = [-Infinity, 2000, 5000, 12500, 30000, 100000];

  amount_el.addEventListener('change', function () {
    let value;

    for (let i = 0; i < levels.length; i++) {
      if (this.value >= levels[i]) {
        value = i;
      }

      level_el.value = value || '';
    }
  });

  level_el.addEventListener('change', function () {
    amount_el.value = this.value ? levels[Number(this.value)] : '';
  });
})();
