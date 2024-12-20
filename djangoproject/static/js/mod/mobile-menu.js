define([
  'jquery', //requires jquery
], function ($) {
  var MobileMenuExport = function (menu) {
    this.menu = $(menu); //menu container
    this.toggleMenuBtn = $('.menu-button');
    this.init();
  };

  MobileMenuExport.prototype = {
    init: function () {
      var self = this;
      self.toggleMenuBtn.on('click', function () {
        self.menu.toggleClass('active');
        self.toggleMenuBtn.toggleClass('active');
      });
    },
  };

  // Export a single instance of our module:
  return new MobileMenuExport('[role="banner"] [role="navigation"]');
});
