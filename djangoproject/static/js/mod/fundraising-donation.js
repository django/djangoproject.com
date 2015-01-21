define([
	'jquery', 'jquery.payment', 'stripe' // requires jquery
	], function($) {

		var numberSelector = 'input[data-stripe="number"]';
		var cvcSelector = 'input[data-stripe="cvc"]';
		var expiresSelector = 'input[data-stripe="expires"]';
		var submitSelector = 'input[type="submit"]';
		var formSelector = '.fundraising-donation';

		function stripeResponseHandler(status, response) {
			var form = $(formSelector);

			if (response.error) {
				// Show the errors on the form
				form.find('.validation-errors').text(response.error.message);
				form.find(submitSelector).prop('disabled', false);
			} else {
				// response contains id and card, which contains additional card details
				var token = response.id;
				// Insert the token into the form so it gets submitted to the server
				form.append($('<input type="hidden" name="stripe_token" />').val(token));
				// and submit
				form.get(0).submit();
			}
		}

		function toggleInputError(check) {
			var selector = check[0],
			toggle = check[1],
			error = check[2],
			errored = false;
			if (toggle) {
				$(selector).removeClass('error');
			} else {
				$(selector).addClass('error');
				var errors = $(formSelector).find('.validation-errors');
				if (errors.text().length > 0) {
					errors.text(errors.text() + ', ' + error);
				} else {
					errors.text(error);
				}
				errored = true;
			}
			return errored;
		}

		var FundraisingDonation = function(form) {
			this.form = $(form); // the floating warning div
			this.init();
		};

		FundraisingDonation.prototype = {
			init: function() {
				var self = this;
				$(document).ready(function() {
					self.form.find('select').on('change', self.setDonation);
					self.form.on('submit', self.submitForm);
					Stripe.setPublishableKey(self.form.data('publishable-key'));
					$(numberSelector).payment('formatCardNumber');
					$(cvcSelector).payment('formatCardCVC');
					$(expiresSelector).payment('formatCardExpiry');
					self.form.find(submitSelector).prop('disabled', false);
				});
			},
			submitForm: function(event) {
				var form = $(this);
				event.preventDefault();
				form.find(submitSelector).prop('disabled', true);
				var expires = $(expiresSelector).payment('cardExpiryVal');
				var card = {
					number: $(numberSelector).val(),
					cvc: $(cvcSelector).val(),
					exp_month: expires.month,
					exp_year: expires.year
				};
				var cardType = $.payment.cardType(card.number);
				var checks = [
					['#id_amount', $('#id_amount').val().length > 0, 'Amount not set'],
					[numberSelector, $.payment.validateCardNumber(card.number), 'Card number invalid'],
					[expiresSelector, $.payment.validateCardExpiry(expires.month, expires.year), 'Expiry invalid'],
					[cvcSelector, $.payment.validateCardCVC(card.cvc, cardType), 'CVC invalid']
				];
				$(formSelector).find('.validation-errors').text('');
				var errored = false;
				$.each(checks , function(index, check) {
					if (toggleInputError(check)) {
						errored = true;
					}
				});
				if (errored) {
					form.find(submitSelector).prop('disabled', false);
				} else {
					// Disable the submit button to prevent repeated clicks
					Stripe.card.createToken(card, stripeResponseHandler);
				}
				return false;
			},
			setDonation: function(event) {
				if ($(this).val() == 'custom'){
					$(this).remove();
					$('.custom-donation').append('<input type="text" name="amount" value="25">').show();
					var input = $('.custom-donation input');
					input.focus();
					// here we're moving the "focus" at the end of the input text
					var tmpStr = input.val();
					input.val('');
					input.val(tmpStr);
				}
			}
		};

		// Export a single instance of our module:
		return new FundraisingDonation(formSelector);
	});
