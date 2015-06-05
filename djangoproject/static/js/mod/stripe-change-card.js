define([
    'jquery', //requires jquery
    'stripe-checkout'
], function ($) {
    var $heroForm = $('.django-hero-form')
    $('.django-hero-form').on('click', '.change-card', function() {
        $this = $(this);
        var donation_id = $this.data('donation_id');
        var handler = StripeCheckout.configure({
            key: $heroForm.data('stripeKey'),
            image: $heroForm.data('stripeIcon'),
            panelLabel: 'Update',
            token: function (token) {
                var csrfToken = $heroForm.find('[name=csrfmiddlewaretoken]').val();
                var data = {
                    'stripe_token': token.id,
                    'donation_id': donation_id,
                    'csrfmiddlewaretoken': csrfToken
                };
                $.ajax({
                    type: "POST",
                    url: $heroForm.data('update-card-url'),
                    data: data,
                    dataType: 'json',
                    success: function (data) {
                        if (data.success) {
                            $this.parent().find('.change-card-result').text('Card updated');
                        } else {
                            alert(data.error);
                        }
                    },
                });
            }
        });

        handler.open({
            name: 'Django Software Foundation',
            currency: 'USD',
            bitcoin: true,
            email: $this.data('donor-email')
        });
    });
})
