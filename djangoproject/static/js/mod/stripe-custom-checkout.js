define([
    'jquery', //requires jquery
    'stripe-checkout'
], function ($) {
    var $donationForm = $('.stripe-custom-checkout');

    var handler = StripeCheckout.configure({
        key: $donationForm.data('stripeKey'),
        image: $donationForm.data('stripeIcon'),
        token: function (token) {
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

        if (interval !== 'onetime' && $donationForm.data('isLoggedIn') === "False"){
            window.location = $donationForm.data('loginUrl') + "?next=" + window.location.pathname;
            return;
        }

        handler.open({
            name: 'Django Software Foundation',
            description: $donationForm.data('campaignName'),
            amount: amountCents,
            currency: 'USD',
            bitcoin: true
        });
    });
});
