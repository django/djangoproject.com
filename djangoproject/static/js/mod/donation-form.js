define([
  'jquery' //requires jquery
  ], function( $ ) {

    var DonationForm = function(form) {
      this.donation_form = $(form); // the floating warning div
      this.init();
    };

    DonationForm.prototype = {
      init: function(){
        var self = this;
        $(document).ready(function () {
          self.donation_form.find('select')[0].addEventListener("change", self.setDonation);
        });
      },
      setDonation: function(event){
        if ($(this).val() == 'custom'){
          $(this).css('display','none');
          $('.custom-donation').css('display','block');
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
    return new DonationForm('.donation-form');
  });
