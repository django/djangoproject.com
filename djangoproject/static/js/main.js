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

  //fundraising heart
  if (hasClass('fundraising-heart')) {
    mods.push('mod/fundraising-heart');
  }

  if (hasClass('dashboard-index')) {
    mods.push('dashboard/index');
  }

  if (hasClass('dashboard-detail')) {
    mods.push('dashboard/detail');
  }

  if (hasClass('stripe-donation')) {
    mods.push('mod/stripe-donation');
  }

  if (hasClass('django-hero-form')) {
    mods.push('mod/stripe-change-card');
  }

  if (hasClass('corporate-membership-join-form')) {
    mods.push('mod/corporate-member-join');
  }

  require(mods);
});
