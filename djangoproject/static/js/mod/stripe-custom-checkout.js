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
            var amount = $donationForm.find('[name=amount]').val();
            var csrfToken = $donationForm.find('[name=csrfmiddlewaretoken]').val();
            var interval = $donationForm.find('[name=interval]').val();
            var data = {
                'stripe_token': token.id,
                'token_type': token.type,
                'receipt_email': token.email,
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
        var csrfToken = $donationForm.find('[name=csrfmiddlewaretoken]').val();
        var recaptchaToken = document.getElementById('id_captcha').value;
        var data = {
            'captcha': recaptchaToken,
            'csrfmiddlewaretoken': csrfToken
        }
        $.ajax({
            type: "POST",
            url: $donationForm.attr('action-for-verify'),
            data: data,
            dataType: 'json',
            success: function (data) {
                if (data.success) {
                    handler.open({
                        name: 'Django Software Foundation',
                        amount: amountCents,
                        currency: 'USD',
                        bitcoin: true,
                        zipCode: true,
                        billingAddress: true
                    });
                } else {
                    alert('There was an error validating that you are not robot. ' +
                          'Sorry. Please refresh the page and try again.');
                }
            }
        })
    });
});
