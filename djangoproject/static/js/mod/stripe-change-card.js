define([
  'jquery', //requires jquery
  'stripe-checkout',
], ($) => {
  const $heroForm = $('.django-hero-form');
  $heroForm.on('click', '.change-card', function () {
    const $this = $(this);
    const donationId = $this.data('donationId');
    const handler = StripeCheckout.configure({
      key: $heroForm.data('stripeKey'),
      image: $heroForm.data('stripeIcon'),
      panelLabel: 'Update',
      token: (token) => {
        const csrfToken = $heroForm.find('[name=csrfmiddlewaretoken]').val();
        const data = {
          stripe_token: token.id,
          donation_id: donationId,
          csrfmiddlewaretoken: csrfToken,
        };
        $.ajax({
          type: 'POST',
          url: $heroForm.data('update-card-url'),
          data: data,
          dataType: 'json',
          success: (data) => {
            if (data.success) {
              $this.parent().find('.change-card-result').text('Card updated');
            } else {
              alert(data.error);
            }
          },
        });
      },
    });

    handler.open({
      name: 'Django Software Foundation',
      currency: 'USD',
      email: $this.data('donor-email'),
    });
  });
});
