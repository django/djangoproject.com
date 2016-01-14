define([
    'jquery' //requires jquery
], function( $ ) {

    var MobileMenuExport = function(menu) {
        this.menu = $(menu); //menu container
        this.init();
    };

    MobileMenuExport.prototype = {
        init: function(){
            var self = this;
            self.menu.addClass('nav-menu-on');
            self.button = $('<div class="menu-button"><i class="icon icon-reorder"></i><span>Menu</span></div>');
            self.button.insertBefore(self.menu);
            self.button.on( 'click', function(){
                self.menu.toggleClass('active');
                self.button.toggleClass('active');
            });
        }
    };

    // Export a single instance of our module:
    return new MobileMenuExport('[role="banner"] [role="navigation"]');
});
