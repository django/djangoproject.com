// Require.js Module Loader - http://requirejs.org
define(function () {
  var mods = [];

  //detect Class function
  function hasClass(className) {
    return !!document.getElementsByClassName(className).length; //return a boolean
  }

  //collapsing list
  if (hasClass('list-collapsing')) {
    mods.push('mod/list-collapsing');
  }

  if (hasClass('stripe-donation')) {
    mods.push('mod/stripe-donation');
  }

  if (hasClass('django-hero-form')) {
    mods.push('mod/stripe-change-card');
  }

  require(mods);
});
