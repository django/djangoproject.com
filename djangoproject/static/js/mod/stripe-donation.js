define([
    'jquery', //requires
    'stripe'
], function($) {
    var $donationForm = $('.stripe-donation');
    var $submitButton = $donationForm.find('.cta');

    $donationForm.on('submit', function (e) {
        e.preventDefault();
        var interval = $donationForm.find('[name=interval]').val();
        var amount = $donationForm.find('[name=amount]').val();
        var csrfToken = $donationForm.find('[name=csrfmiddlewaretoken]').val();
        var data = {
            'interval': interval,
            'amount': amount,
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
    });

});
