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

				// Here we are doing something really annoying, we catch clicks on
				// internal anchors and scroll to the right place of the page.
				// This is only needed because we want to show the developement version
				// warning on top.
				// First handle the case in which someone clicks on a link
				 $('a[href*=#]').click(function () {
					// check to see if this is an internal link, sigh.
					if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') &&
						location.hostname == this.hostname) {
						// get the link target, use the weird id= query since it escapes dots
						var target = $("[id='" + this.hash.slice(1) + "']");
						// calculate the offset
						var targetOffset = target.offset().top - self.warning.height() - 20;
						// scroll to the place, there is probably a better way
						setTimeout(function () {
						  $('html,body').scrollTop(targetOffset);
						}, 50);
					}
				});
				// this is the janky thing, there is probably a better way
				setTimeout(function () {
					// is there a hash in the current window's location?
					if (window.location.hash) {
						// again, get the target
						var target = $("[id='" + window.location.hash.slice(1) + "']");
						// calculate the offset
						var targetOffset = target.offset().top - self.warning.height() - 20;
						// scroll to the place
						$('html,body').scrollTop(targetOffset);
					}
				// use a delay that should work on all modern computers. should, not will
				}, 50);
			});
		}
	};

	// Export a single instance of our module:
	return new FloatingWarning('.doc-floating-warning');
});
