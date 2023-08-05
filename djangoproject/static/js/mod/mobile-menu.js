define([
    'jquery' //requires jquery
], function( $ ) {

    var MobileMenuExport = function(menu) {
        this.menu = $(menu); //menu container
        this.menuBtn = $('.mobile-toggle'); // toggle dark mode icon
        this.init();
    };

    MobileMenuExport.prototype = {
        init: function(){
            var self = this;
            self.menu.addClass('nav-menu-on');
            self.button = $('<div class="menu-button"><button class="icon icon-reorder" style="background-color: transparent; color: white; border: none;"></button><span>Menu</span></div>');
            self.button.insertBefore(self.menuBtn);
            self.button.on( 'click', function(){
                self.menu.toggleClass('active');
                self.button.toggleClass('active');
            });
        }
    };

    // Export a single instance of our module:
    return new MobileMenuExport('[role="banner"] [role="navigation"]');
});
