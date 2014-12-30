define([
	'jquery.inview' //required inview plugin
], function( $ ) {

	var FeatureList = function(list) {
		this.list = $(list);
		this.init();
	};

	FeatureList.prototype = {
		init: function(){
			this.icons = this.list.find('dt i'); //go get icons
			this.icons.bind('inview', function(event, isInView, visiblePartX, visiblePartY) {
				if (isInView && visiblePartY != 'top' && visiblePartY != 'bottom') { // element completely visible
					$(this).addClass('inview'); //new class
				}
			});
		}
	};

	// Export a single instance of our module:
	return new FeatureList('.list-features');
});