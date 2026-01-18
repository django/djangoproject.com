define([
  'jquery', //requires
  'stripe',
], ($) => {
  const $donationForm = $('.stripe-donation');

  function postToStripe(recaptchaToken) {
    const interval = $donationForm.find('[name=interval]').val();
    const amount = $donationForm.find('[name=amount]').val();
    const csrfToken = $donationForm.find('[name=csrfmiddlewaretoken]').val();
    const data = {
      interval: interval,
      amount: amount,
      captcha: recaptchaToken,
      csrfmiddlewaretoken: csrfToken,
    };
    $.ajax({
      type: 'POST',
      url: $donationForm.attr('action-for-donation-session'),
      data: data,
      dataType: 'json',
      success: (data) => {
        console.info(data);
        if (data.success) {
          const stripe = Stripe($donationForm.data('stripeKey'));
          return stripe.redirectToCheckout({ sessionId: data.sessionId });
        } else {
          msg = 'There was an error setting up your donation. ';
          if (data.error.amount) {
            msg += data.error.amount;
          } else {
            msg += 'Sorry. Please refresh the page and try again.';
          }
          alert(msg);
        }
      },
    });
  }

  // django-recaptcha==4.0.0 adds a `submit` event listener to the form that
  // ends up calling form.submit(), therefore bypassing our own event listener.
  // As a workaround, we remove their event listener and replace it with our own.
  if (globalThis.recaptchaFormSubmit !== undefined) {
    $donationForm[0].removeEventListener(
      'submit',
      globalThis.recaptchaFormSubmit,
    );
  }
  $donationForm.on('submit', (e) => {
    e.preventDefault();
    let captcha_input = document.getElementById('id_captcha'),
      public_key = captcha_input.getAttribute('data-sitekey');
    // Validate token on form submit.
    // NOTE: the `action` key must match the one defined on the widget.
    grecaptcha.execute(public_key, { action: 'form' }).then((token) => {
      captcha_input.value = token;
      console.info('reCAPTCHA validated. Posting to stripe...');
      postToStripe(token);
    });
  });
});
