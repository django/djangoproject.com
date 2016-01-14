define([
    'jquery' //requires jquery
], function( $ ) {

    var VersionSwitcher = function(switcher) {
        this.switcher = $(switcher); // the version switcher
        this.init();
    };

    VersionSwitcher.prototype = {
        init: function(){
            var self = this;
            $(document).ready(function () {
                // Propagate the fragment identifier to the links in the version switcher
                self.switcher.find('a').on('click', function () {
                    var hrefWithoutFragment = this.href.split('#')[0];
                    this.href = hrefWithoutFragment + window.location.hash;
                    // do nothing and let the event bubble up
                });
                // Make version switcher clickable for touch devices
                self.switcher.find('li.current').on('click', function () {
                    self.switcher.find('li.other').toggleClass('hover-on');
                });
            });
        }
    };

    // Export a single instance of our module:
    return new VersionSwitcher('#doc-versions');
});
