QUnit.config.reorder = false;

window['jQuery 1.6'].each(['jQuery 1.4', 'jQuery 1.5', 'jQuery 1.6', 'jQuery 1.7', 'jQuery 1.8'], function(i, version) {
  var jQuery  = window[version],
      $       = jQuery;

  module('jquery.inview - ' + version, {
    setup: function() {
      $(window).scrollTop(0).scrollLeft(0);

      this.size = 20000;
      this.container = $('<div>', {
        "class": 'test-container'
      }).appendTo("body");

      this.element = $('<div>', {
        html: 'testing ...',
        "class": 'test-element'
      }).css({
        background: '#eee',
        width:      '50px',
        height:     '50px',
        position:   'absolute'
      });

      this.element2 = this.element.clone();
    },

    teardown: function() {
      $(window).scrollTop(0).scrollLeft(0);

      this.container.remove();
      this.element.remove();
    }
  });


  asyncTest('Check vertical scrolling', function() {
    expect(5);

    var element = this.element,
        firstCall,
        secondCall,
        thirdCall,
        inView;

    element.css({ left: 0, top: this.size - 50 + 'px' });
    element.appendTo('body');
    element.bind('inview.firstCall', function() { firstCall = true; });

    setTimeout(function() {
      $(window).scrollTop(0).scrollLeft(0);
      ok(!firstCall, 'inview shouldn\'t be triggered initially when the element isn\'t in the viewport');
      element.unbind('inview.firstCall');
      element.bind('inview.secondCall', function(event, inViewParam) {
        secondCall = true;
        inView = inViewParam;
      });

      $(window).scrollTop(9999999);

      setTimeout(function() {

        ok(secondCall, 'Triggered handler after element appeared in viewport');
        ok(inView, 'Parameter, indicating whether the element is in the viewport, is set to "true"');
        element.unbind('inview.secondCall');
        element.bind('inview.thirdCall', function(event, inViewParam) {
          thirdCall = true;
          inView = inViewParam;
        });

        $(window).scrollTop(0).scrollLeft(0);

        setTimeout(function() {
          ok(thirdCall, 'Triggered handler after element disappeared in viewport');
          strictEqual(inView, false, 'Parameter, indicating whether the element is in the viewport, is set to "false"');
          start();
        }, 1000);

      }, 1000);

    }, 1000);
  });


  asyncTest('Check horizontal scrolling', function() {
    expect(5);

    var element = this.element,
        firstCall,
        secondCall,
        thirdCall,
        inView;

    element.css({ top: 0, left: this.size - 50 + 'px' });
    element.appendTo('body');
    element.bind('inview.firstCall', function() { firstCall = true; });

    setTimeout(function() {
      $(window).scrollTop(0).scrollLeft(0);

      ok(!firstCall, 'inview shouldn\'t be triggered initially when the element isn\'t in the viewport');
      element.unbind('inview.firstCall');
      element.bind('inview.secondCall', function(event, inViewParam) {
        secondCall = true;
        inView = inViewParam;
      });

      $(window).scrollLeft(9999999);

      setTimeout(function() {

        ok(secondCall, 'Triggered handler after element appeared in viewport');
        ok(inView, 'Parameter, indicating whether the element is in the viewport, is set to "true"');
        element.unbind('inview.secondCall');
        element.bind('inview.thirdCall', function(event, inViewParam) {
          thirdCall = true;
          inView = inViewParam;
        });

        $(window).scrollTop(0).scrollLeft(0);

        setTimeout(function() {
          ok(thirdCall, 'Triggered handler after element disappeared in viewport');
          strictEqual(inView, false, 'Parameter, indicating whether the element is in the viewport, is set to "false"');
          start();
        }, 1000);

      }, 1000);

    }, 1000);
  });


  asyncTest('Move element into viewport without scrolling', function() {
    expect(3);

    var element = this.element, calls = 0;

    element
      .css({ left: '-500px', top: 0 })
      .appendTo('body')
      .bind('inview', function(event) { calls++; });

    setTimeout(function() {

      equal(calls, 0, 'Callback hasn\'t been fired since the element isn\'t in the viewport');
      element.css({ left: 0 });

      setTimeout(function() {

        equal(calls, 1, 'Callback has been fired after the element appeared in the viewport');
        element.css({ left: '10000px' });

        setTimeout(function() {

          equal(calls, 2, 'Callback has been fired after the element disappeared from viewport');
          start();

        }, 1000);

      }, 1000);

    }, 1000);
  });


  asyncTest('Check whether element which isn\'t in the dom tree triggers the callback', function() {
    expect(0);

    this.element.bind('inview', function(event, isInView) {
      ok(false, 'Callback shouldn\'t be fired since the element isn\'t even in the dom tree');
      start();
    });

    setTimeout(function() { start(); }, 1000);
  });


  asyncTest('Check whether element which is on the top outside of viewport is not firing the event', function() {
    expect(0);

    this.element.bind('inview', function(event, isInView) {
      ok(false, 'Callback shouldn\'t be fired since the element is outside of viewport');
      start();
    });

    this.element.css({
      top: '-50px',
      left: '50px'
    }).appendTo('body');

    setTimeout(function() { start(); }, 1000);
  });


  asyncTest('Check whether element which is on the left outside of viewport is not firing the event', function() {
    expect(0);

    this.element.bind('inview', function(event, isInView) {
      ok(false, 'Callback shouldn\'t be fired since the element is outside of viewport');
      start();
    });

    this.element.css({
      top: '50px',
      left: '-50px'
    }).appendTo('body');

    setTimeout(function() { start(); }, 1000);
  });


  asyncTest('Check visiblePartX & visiblePartY parameters #1', function() {
    expect(2);

    this.element.css({
      top: '-25px',
      left: '-25px'
    }).appendTo('body');

    this.element.bind('inview', function(event, isInView, visiblePartX, visiblePartY) {
      equal(visiblePartX, 'right', 'visiblePartX has correct value');
      equal(visiblePartY, 'bottom', 'visiblePartY has correct value');
      start();
    });
  });


  asyncTest('Check visiblePartX & visiblePartY parameters #2', function() {
    expect(2);

    this.element.css({
      top: '0',
      left: '-25px'
    }).appendTo('body');

    this.element.bind('inview', function(event, isInView, visiblePartX, visiblePartY) {
      equal(visiblePartX, 'right', 'visiblePartX has correct value');
      equal(visiblePartY, 'both', 'visiblePartY has correct value');
      start();
    });
  });


  asyncTest('Check visiblePartX & visiblePartY parameters #3', function() {
    expect(2);

    this.element.css({
      top: '0',
      left: '0'
    }).appendTo('body');

    this.element.bind('inview', function(event, isInView, visiblePartX, visiblePartY) {
      equal(visiblePartX, 'both', 'visiblePartX has correct value');
      equal(visiblePartY, 'both', 'visiblePartY has correct value');
      start();
    });
  });


  asyncTest('Check "live" events', function() {
    expect(3);
    
    var that = this,
        elems = $("body .test-container > div.test-element");
    elems.live("inview", function(event) {
      elems.die("inview");
      ok(true, "Live event correctly fired");
      equal(event.currentTarget, that.element[0], "event.currentTarget correctly set");
      equal(this, that.element[0], "Handler bound to target element");
      start();
    });

    this.element.css({
      top: '0',
      left: '0'
    }).appendTo(this.container);
  });


  asyncTest('Check "delegate" events', function() {
    expect(3);

    var that = this;
    this.container.delegate(".test-element", "inview", function(event) {
      ok(true, "Delegated event correctly fired");
      equal(event.currentTarget, that.element[0], "event.currentTarget correctly set");
      equal(this, that.element[0], "Handler bound to target element");
      start();
    });

    this.element.css({
      top: '0',
      left: '0'
    }).appendTo(this.container);
  });


  asyncTest('Check namespaced "delegate" events', function() {
    expect(1);

    this.container.delegate(".test-element", "inview.foo", function(event) {
      ok(true, "Delegated event correctly fired");
      start();
    });

    this.element.css({
      top: '0',
      left: '0'
    }).appendTo(this.container);
  });


  asyncTest('Check multiple elements', function() {
    expect(2);

    var i = 0;

    this.element.add(this.element2).css({
      top: '0',
      left: '0'
    }).appendTo(this.container);

    $('.test-element').bind('inview', function() {
      ok(true);
      if (++i == 2) {
        start();
      }
    });
  });
  
  if (!("ontouchstart" in window)) {
    asyncTest('Scroll to element via focus()', function() {
      // This test will fail on iOS

      expect(1);

      var $input = $("<input>").css({
        position: "absolute",
        top: "7000px",
        left: "5000px"
      }).appendTo(this.container);

      $input.bind('inview', function() {
        ok(true);
        $input.remove();
        start();
      });

      setTimeout(function() {
        $input.focus();
      }, 1000);
    });
  }
});
