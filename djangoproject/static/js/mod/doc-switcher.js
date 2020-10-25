define([
    'jquery' //requires jquery
], function( $ ) {

    var DocSwitcher = function(switchers) {
        this.switchers = $(switchers);
        this.init();
    };

    DocSwitcher.prototype = {
        init: function(){
            var self = this;
            $(document).ready(function () {
                // Make version switcher clickable for touch devices

                self.switchers.find('li.current').on('click', function () {
                    $(this).closest("ul").toggleClass('open');
                });
            });
        }
    };

    // Export a single instance of our module:
    return new DocSwitcher('.doc-switcher');
});
