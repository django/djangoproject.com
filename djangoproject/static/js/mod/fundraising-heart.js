define([
	'jquery',
], function( $ ) {

	var maroon = '#ad1d45';
	var amaranth = '#d9195c';
	var cerise = '#d62d75';
	var razzmatazz = '#ee2178';
	var illusion = '#f7b0cf';
	var pixels = [
			// Row 1
			{x:1, y: 0, color: maroon},
			{x:2, y: 0, color: amaranth},
			{x:4, y: 0, color: amaranth},
			{x:5, y: 0, color: cerise},

			// Row 2
			{x:0, y: 1, color: amaranth},
			{x:1, y: 1, color: razzmatazz},
			{x:2, y: 1, color: razzmatazz},
			{x:3, y: 1, color: amaranth},
			{x:4, y: 1, color: razzmatazz},
			{x:5, y: 1, color: illusion},
			{x:6, y: 1, color: maroon},

			// Row 3
			{x:0, y: 2, color: cerise},
			{x:1, y: 2, color: amaranth},
			{x:2, y: 2, color: amaranth},
			{x:3, y: 2, color: maroon},
			{x:4, y: 2, color: amaranth},
			{x:5, y: 2, color: cerise},
			{x:6, y: 2, color: maroon},

			// Row 4
			{x:1, y: 3, color: maroon},
			{x:2, y: 3, color: razzmatazz},
			{x:3, y: 3, color: amaranth},
			{x:4, y: 3, color: razzmatazz},
			{x:5, y: 3, color: amaranth},

			// Row 5
			{x:2, y: 4, color: amaranth},
			{x:3, y: 4, color: cerise},
			{x:4, y: 4, color: amaranth},

			// Row 6
			{x:3, y: 5, color: razzmatazz},
		];

	function getRandomElement(array) {
		return array[Math.floor(Math.random() * array.length)];
	}

	var Heart = function(heart) {
		this.heart = $(heart);
		if (Modernizr.svg) {
			this.init();
		}
	};

	Heart.prototype = {
		init: function() {
			this.pixels = pixels.map(function (pixel) {
				return new Rectangle(pixel);
			});
			this.fadePixels();
			this.draw();
			var heart = this;
			window.setInterval(function () {
				heart.moveFadedPixel();
			}, 5000);
		},
		fadePixels: function () {
			var percent = this.heart.data('percent');
			var fadedCount = Math.ceil(this.pixels.length * (100 - percent) / 100);
			for (var i = 0; i < fadedCount; i++) {
				getRandomElement(this.visiblePixels()).hide();
			}
		},
		hiddenPixels: function () {
			return this.pixels.filter(function (p) { return p.isHidden; });
		},
		visiblePixels: function () {
			return this.pixels.filter(function (p) { return !p.isHidden; });
		},
		moveFadedPixel: function () {
			var hiddenPixels = this.hiddenPixels();
			var visiblePixels = this.visiblePixels();
			if (hiddenPixels.length && visiblePixels.length) {
				var oldPixel = getRandomElement(hiddenPixels).show();
				var newPixel = getRandomElement(visiblePixels).hide();
			}
		},
		draw: function() {
			this.pixels.forEach(function (p) {
				document.getElementById('pixels').appendChild(p.element);
			});
		}
	};

	var Rectangle = function (opts) {
	var namespace = 'http://www.w3.org/2000/svg';
		this.element = document.createElementNS(namespace, 'rect');
		this.size = 71;
		this.init(opts);
	};

	Rectangle.prototype = {
		init: function(opts) {
			this.isHidden = false;
			this.setAttr('x', opts.x * this.size);
			this.setAttr('y', opts.y * this.size);
			this.setAttr('width', this.size);
			this.setAttr('height', this.size);
			this.setAttr('fill', opts.color);
		},
		setAttr: function(name, value) {
			this.element.setAttributeNS(null, name, value);
		},
		hide: function () {
			this.isHidden = true;
			this.setAttr('class', 'faded');
		},
		show: function () {
			this.isHidden = false;
			this.setAttr('class', '');
		}
	};

	// Export a single instance of our module:
	return new Heart('.fundraising-heart');
});
