define([
    'jquery', //requires jquery
    'stripe-checkout'
], function($) {
    var $heroForm = $('.django-hero-form');
    $heroForm.on('click', '.change-card', function() {
        $this = $(this);
        var donationId = $this.data('donationId');
        var handler = StripeCheckout.configure({
            key: $heroForm.data('stripeKey'),
            image: $heroForm.data('stripeIcon'),
            panelLabel: 'Update',
            token: function (token) {
                var csrfToken = $heroForm.find('[name=csrfmiddlewaretoken]').val();
                var data = {
                    'stripe_token': token.id,
                    'donation_id': donationId,
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
            email: $this.data('donor-email')
        });
    });
})
