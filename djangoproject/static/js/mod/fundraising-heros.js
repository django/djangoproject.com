define([
	'jquery', //requires jquery
	'jquery.unveil' // requires unveil.js
	], function( $ ) {
		// This will makes the Django hero images only be loaded
		// when scrolled to.

		// Load images 200 pixels before they become visible,
		// assumes an image size of 170 px plus some margin
		var threshold = 200;

		var FundraisingHeros = function(images) {
			this.images = $(images); // the heros images
			this.init();
		};

		FundraisingHeros.prototype = {
			init: function(){
				var self = this;
				$(document).ready(function() {
					self.images.unveil(threshold);
				});
			},

		// Export a single instance of our module:
		return new FundraisingHeros('.hero-logo img');
});
