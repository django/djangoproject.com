define([
    'jquery' //requires jquery
    ], function( $ ) {

        var FundraisingIndex = function(form) {
            this.form = $(form); // the floating warning div
            this.init();
        };

        FundraisingIndex.prototype = {
            init: function(){
                var self = this;
                $(document).ready(function() {
                    self.form.find('select').on("change", self.setDonation);
                    self.form.find('select').on("change", self.setDonateButtonText).change();
                });
            },
            setDonation: function(event){
                if ($(this).val() == 'custom'){
                    $(this).remove();
                    $('.custom-donation').append('<input type="number" name="amount" value="25">').show();
                    var input = $('.custom-donation input');
                    input.focus();
                    // here we're moving the "focus" at the end of the input text
                    var tmpStr = input.val();
                    input.val('');
                    input.val(tmpStr);
                }
            },
            setDonateButtonText: function(event) {
                var text = 'Donate';
                var interval = $('#id_interval').val();
                if (interval != 'onetime') {
                    text += ' ' + interval;
                }
                $('#donate-button').val(text);
            }
        };

        // Export a single instance of our module:
        return new FundraisingIndex('.fundraising-index form');
    });
