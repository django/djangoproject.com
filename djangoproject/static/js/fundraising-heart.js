(() => {
  const maroon = '#ad1d45';
  const amaranth = '#d9195c';
  const cerise = '#d62d75';
  const razzmatazz = '#ee2178';
  const illusion = '#f7b0cf';
  const pixels = [
    // Row 1
    { x: 1, y: 0, color: maroon },
    { x: 2, y: 0, color: amaranth },
    { x: 4, y: 0, color: amaranth },
    { x: 5, y: 0, color: cerise },

    // Row 2
    { x: 0, y: 1, color: amaranth },
    { x: 1, y: 1, color: razzmatazz },
    { x: 2, y: 1, color: razzmatazz },
    { x: 3, y: 1, color: amaranth },
    { x: 4, y: 1, color: razzmatazz },
    { x: 5, y: 1, color: illusion },
    { x: 6, y: 1, color: maroon },

    // Row 3
    { x: 0, y: 2, color: cerise },
    { x: 1, y: 2, color: amaranth },
    { x: 2, y: 2, color: amaranth },
    { x: 3, y: 2, color: maroon },
    { x: 4, y: 2, color: amaranth },
    { x: 5, y: 2, color: cerise },
    { x: 6, y: 2, color: maroon },

    // Row 4
    { x: 1, y: 3, color: maroon },
    { x: 2, y: 3, color: razzmatazz },
    { x: 3, y: 3, color: amaranth },
    { x: 4, y: 3, color: razzmatazz },
    { x: 5, y: 3, color: amaranth },

    // Row 5
    { x: 2, y: 4, color: amaranth },
    { x: 3, y: 4, color: cerise },
    { x: 4, y: 4, color: amaranth },

    // Row 6
    { x: 3, y: 5, color: razzmatazz },
  ];

  class Heart {
    constructor(selector) {
      this.heart = document.querySelector(selector);
      this.init();
    }

    init() {
      this.pixels = pixels.map((pixel) => {
        return new Rectangle(pixel);
      });
      this.fadePixels();
      this.draw();
      const heart = this;
    }

    fadePixels() {
      let pixels;
      const percent = this.heart.dataset.percent;
      const fadedCount = Math.ceil(
        (this.pixels.length * (100 - percent)) / 100,
      );
      for (let i = 0; i < fadedCount; i++) {
        pixels = this.visiblePixels();
        pixels[0].hide();
      }
    }

    hiddenPixels() {
      return this.pixels.filter((p) => {
        return p.isHidden;
      });
    }

    visiblePixels() {
      return this.pixels.filter((p) => {
        return !p.isHidden;
      });
    }

    draw() {
      this.pixels.forEach((p) => {
        document.getElementById('pixels').appendChild(p.element);
      });
    }
  }

  class Rectangle {
    constructor(opts) {
      const namespace = 'http://www.w3.org/2000/svg';
      this.element = document.createElementNS(namespace, 'rect');
      this.size = 71;
      this.init(opts);
    }

    init(opts) {
      this.isHidden = false;
      this.setAttr('x', opts.x * this.size);
      this.setAttr('y', opts.y * this.size);
      this.setAttr('width', this.size);
      this.setAttr('height', this.size);
      this.setAttr('fill', opts.color);
      this.element.style.animationDelay = `${3 * Math.random()}s`;
    }

    setAttr(name, value) {
      this.element.setAttributeNS(null, name, value);
    }

    hide() {
      this.isHidden = true;
      this.setAttr('class', 'faded');
    }

    show() {
      this.isHidden = false;
      this.setAttr('class', '');
    }
  }

  new Heart('.fundraising-heart');
})();
