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
                var search_form_input = self.search_form.find('input');
                var raw_placeholder = search_form_input.attr('placeholder');
                var kbd_shortcut_suffix = "Ctrl + K";
                if (navigator.userAgent.indexOf("Mac") !== -1) kbd_shortcut_suffix = "⌘ + K";
                search_form_input.attr('placeholder', `${raw_placeholder} (${kbd_shortcut_suffix})`);

                $(window).keydown(function(e) {
                    if (e.key === 'k' && e.ctrlKey && $('input:focus, textarea:focus').length === 0) {
                        search_form_input.focus().select();
                        return false;
                    }
                });
            });
        }
    };

    // Export a single instance of our module:
    return new SearchForm('.search');
});
