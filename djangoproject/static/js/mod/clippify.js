define(['jquery'], function ($) {
  $('.code-block-caption').each(function () {
    var header = $(this);
    var wrapper = header.parent();
    var code = $('.highlight', wrapper);
    var btn = $('<span class="btn-clipboard" title="Copy this code">');
    btn.append('<i class="icon icon-clipboard">');
    btn.data('clipboard-text', $.trim(code.text()));
    header.append(btn);
  });
  // For Django 2.0 docs and older.
  $('.snippet').each(function () {
    var code = $('.highlight', this);
    var btn = $('<span class="btn-clipboard" title="Copy this code">');
    var header = $('.snippet-filename', this);

    btn.append('<i class="icon icon-clipboard">');
    btn.data('clipboard-text', $.trim(code.text()));
    header.append(btn);
  });
  $('.btn-clipboard').click(function () {
    var btn = $(this);
    var text = btn.data('clipboard-text');

    function on_success(el) {
      var success = $('<span class="clipboard-success">').text('Copied!');
      success.prependTo(btn).delay(1000).fadeOut();
    }

    function on_error(el) {
      var success = $('<span class="clipboard-success">').text(
        'Could not copy!',
      );
      success.prependTo(btn).delay(5000).fadeOut();
    }

    navigator.clipboard.writeText(text).then(on_success, on_error);
  });
});
