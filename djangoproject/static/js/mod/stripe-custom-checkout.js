define([
    'jquery', //requires jquery
    'stripe-checkout'
], function ($) {
    var $donationForm = $('.stripe-custom-checkout');
    var $submitButton = $donationForm.find('.cta');

    var handler = StripeCheckout.configure({
        key: $donationForm.data('stripeKey'),
        image: $donationForm.data('stripeIcon'),
        token: function (token) {
            $submitButton.prop('disabled', true).addClass('disabled');
            var campaign = $donationForm.find('[name=campaign]').val();
            var amount = $donationForm.find('[name=amount]').val();
            var csrfToken = $donationForm.find('[name=csrfmiddlewaretoken]').val();
            var interval = $donationForm.find('[name=interval]').val();
            var data = {
                'stripe_token': token.id,
                'receipt_email': token.email,
                'campaign': campaign,
                'amount': amount,
                'interval': interval,
                'csrfmiddlewaretoken': csrfToken
            };

            $.ajax({
                type: "POST",
                url: $donationForm.attr('action'),
                data: data,
                dataType: 'json',
                success: function (data) {
                    if (data.success) {
                        window.location = data.redirect;
                    } else {
                        $submitButton.prop('disabled', false).removeClass('disabled');
                        alert(data.error);
                    }
                }
            })
        }
    });

    // Close Checkout on page navigation
    $(window).on('popstate', function () {
        handler.close();
    });

    $donationForm.on('submit', function (e) {
        e.preventDefault();
        var interval = $donationForm.find('[name=interval]').val();
        var amountDollars = $donationForm.find('[name=amount]').val();
        var amountCents = parseFloat(amountDollars) * 100;

        handler.open({
            name: 'Django Software Foundation',
            description: $donationForm.data('campaignName'),
            amount: amountCents,
            currency: 'USD',
            bitcoin: true,
            zipCode: true,
            billingAddress: true
        });
    });
});
