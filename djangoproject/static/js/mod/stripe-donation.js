define([
    'jquery', //requires
    'stripe'
], function($) {
    var $donationForm = $('.stripe-donation');

    function postToStripe(recaptchaToken) {
        var interval = $donationForm.find('[name=interval]').val();
        var amount = $donationForm.find('[name=amount]').val();
        var csrfToken = $donationForm.find('[name=csrfmiddlewaretoken]').val();
        var data = {
            'interval': interval,
            'amount': amount,
            'captcha': recaptchaToken,
            'csrfmiddlewaretoken': csrfToken
        }
        $.ajax({
            type: "POST",
            url: $donationForm.attr('action-for-donation-session'),
            data: data,
            dataType: 'json',
            success: function (data) {
                console.log(data)
                if (data.success) {
                    var stripe = Stripe($donationForm.data('stripeKey'))
                    return stripe.redirectToCheckout({sessionId: data.sessionId})
                } else {
                    msg = 'There was an error setting up your donation. '
                    if (data.error.amount) {
                        msg += data.error.amount
                    } else {
                        msg += 'Sorry. Please refresh the page and try again.'
                    }
                    alert(msg);
                }
            }
        })
    };

    // django-recaptcha==4.0.0 adds a `submit` event listener to the form that ends up calling
    // form.sumit(), therefore bypassing our own event listener.
    // As a workaround, we remove their event listener and replace it with our own
    if (window.recaptchaFormSubmit !== undefined) {
        $donationForm[0].removeEventListener("submit", window.recaptchaFormSubmit);
    }
    $donationForm.on('submit', function (e) {
        e.preventDefault();
        // validate token on form submit
        let public_key = document.getElementById("id_captcha").getAttribute('data-sitekey');
        grecaptcha.execute(public_key, {action: 'form'}).then(function(token) {
            console.log("reCAPTCHA validated. Posting to stripe...");
            postToStripe(token);
        });
    });

});
