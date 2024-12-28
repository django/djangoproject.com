// Require.js Module Loader - http://requirejs.org
define(function () {
  var mods = [
    'mod/mobile-menu', // require mobile menu automatically
  ];

  //detect Class function
  function hasClass(className) {
    return !!document.getElementsByClassName(className).length; //return a boolean
  }

  //feature list
  if (hasClass('list-features')) {
    mods.push('mod/list-feature');
  }

  //collapsing list
  if (hasClass('list-collapsing')) {
    mods.push('mod/list-collapsing');
  }

  if (hasClass('doc-floating-warning')) {
    mods.push('mod/floating-warning');
  }

  //fundraising heart
  if (hasClass('fundraising-heart')) {
    mods.push('mod/fundraising-heart');
  }
  //fundraising donation form
  if (hasClass('fundraising-index')) {
    mods.push('mod/fundraising-index');
  }

  if (hasClass('dashboard-index')) {
    mods.push('dashboard/index');
  }

  if (hasClass('dashboard-detail')) {
    mods.push('dashboard/detail');
  }

  // search form
  if (hasClass('search')) {
    mods.push('mod/search-key');
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

  if (hasClass('code-block-caption') || hasClass('snippet')) {
    mods.push('mod/clippify');
  }

  if (hasClass('console-block')) {
    mods.push('mod/console-tabs');
  }

  require(mods);
});
