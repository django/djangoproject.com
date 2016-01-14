define([
    'jquery' //requires jquery
], function( $ ) {

    var FloatingWarning = function(warning) {
        this.warning = $(warning); // the floating warning div
        this.init();
    };

    FloatingWarning.prototype = {
        init: function(){
            var self = this;
            $(document).ready(function () {
                // Clone warning to top of document, without fixed positioning,
                // to force correct spacing of header.
                self.warning.clone().prependTo('body').css('position', 'relative');

                setTimeout(function () {
                    self.scroll(window.location.hash, self.warning);
                }, 50); // use a delay that should work on all modern computers. should, not will

                // use something nicer
                $(window).on('hashchange', function() {
                    self.scroll(window.location.hash, self.warning);
                });
            });
        },
        scroll: function(hash, warning) {
            // is there a hash in the current window's location?
            if (hash) {
                // again, get the target
                var target = $("[id='" + hash.slice(1) + "']");
                if (target.length) {
                    // calculate the offset
                    var targetOffset = target.offset().top - warning.height() - 20;
                    // scroll to the place
                    $('html,body').scrollTop(targetOffset);
                }
            }
        }
    };

    // Export a single instance of our module:
    return new FloatingWarning('.doc-floating-warning');
});
