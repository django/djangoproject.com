define([
    'jquery' //requires jquery
], function( $ ) {

    var SearchForm = function(search_form) {
        this.search_form = $(search_form); // the search form
        this.init();
    };

    SearchForm.prototype = {
        init: function(){
            var self = this;
            $(document).ready(function () {
                $(window).keypress(function(e) {
                    if ($('input:focus, textarea:focus').length === 0 &&
                            e.which === 47) {  // The slash is 47.
                        self.search_form.find('input').focus().select();
                        return false;
                    }
                });
            });
        }
    };

    // Export a single instance of our module:
    return new SearchForm('.search');
});
