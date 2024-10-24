define([
    'jquery' //requires jquery
], function( $ ) {
    const SearchForm = function(search_form) {
        this.search_form = $(search_form); // the search form
        this.init();
    };

    SearchForm.prototype = {
        init: function(){
            const self = this;
            $(document).ready(function () {
                const search_form_input = self.search_form.find('input');
                const raw_placeholder = search_form_input.attr('placeholder');
                const shortcut = navigator.userAgent.indexOf("Mac") === -1 ? "Ctrl + K" : "⌘ + K";
                search_form_input.attr('placeholder', `${raw_placeholder} (${shortcut})`);

                $(window).keydown(function(e) {
                    if ((e.metaKey || e.ctrlKey) && e.key === 'k' && $('input:focus, textarea:focus').length === 0) {
                        const warning_banner_height = $('#dev-warning').outerHeight() || 0;
                        const search_form_input_top = search_form_input.offset().top;
                        const scroll_to_position = search_form_input_top - warning_banner_height;
                        search_form_input.focus().select();
                        window.scrollTo({
                            top: scroll_to_position,
                            behavior: 'smooth'
                        });
                        return false;
                    }
                });
            });
        }
    };

    // Export a single instance of our module:
    return new SearchForm('.search');
});
