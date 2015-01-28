Modernizr Retina Test
=====================

A simple and quick Modernizr test for retina / high resolution / high pixel density. Should run in less than half a milisecond.

```js
/**
 * Modernizr test for retina / high resolution / high pixel density
 *
 * @author Joao Cunha
 * @license MIT
 */
 
Modernizr.addTest('hires', function() {
    // starts with default value for modern browsers
    var dpr = window.devicePixelRatio ||
 
    // fallback for IE
        (window.screen.deviceXDPI / window.screen.logicalXDPI) ||
 
    // default value
        1;
 
    return !!(dpr > 1);
});
```
