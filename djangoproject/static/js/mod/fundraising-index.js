define([
	'jquery' //requires jquery
	], function( $ ) {

		var FundraisingIndex = function(form) {
			this.form = $(form); // the floating warning div
			this.init();
		};

		FundraisingIndex.prototype = {
			init: function() {
				var self = this;
				$(document).ready(function() {
					// We'll check if we need to go to display the "custom amount"
					// field both on page ready and everytime the select change

					self.form.find('select').on("change", function(){
						self.setDonation(this);
					});
					self.setDonation();
				});
			},
			setDonation: function(select) {
				if (select === undefined) {
					select = this.form.find('select[name=amount]')
				}
				var $select = $(select);

				if ($select.val() == 'custom') {
					$select.hide();
					$('.custom-donation').show();
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
		return new FundraisingIndex('.fundraising-index form');
	});
