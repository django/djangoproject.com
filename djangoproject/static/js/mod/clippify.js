define(['jquery', 'clipboard'], function($, Clipboard) {
    $('.code-block-caption').each(function() {
        var header = $(this);
        var wrapper = header.parent();
        var code = $('.highlight', wrapper);
		var copy_str = gettext("Copy this code");
        var btn = $('<span class="btn-clipboard" title="' + copy_str + '">');
        btn.append('<i class="icon icon-clipboard">');
        btn.data('clipboard-text', $.trim(code.text()));
        header.append(btn);
    });
    // For Django 2.0 docs and older.
    $('.snippet').each(function() {
        var code = $('.highlight', this);
		var copy_str = gettext("Copy this code");
        var btn = $('<span class="btn-clipboard" title="' + copy_str + '">');
        var header = $('.snippet-filename', this);

        btn.append('<i class="icon icon-clipboard">');
        btn.data('clipboard-text', $.trim(code.text()));
        header.append(btn);
    });
    var clip = new Clipboard('.btn-clipboard', {
        'text': function(trigger) {
            return $(trigger).data('clipboard-text');
        }
    });
    clip.on('success', function(e) {
		var copy_str = gettext("Copied!");
        var success = $('<span class="clipboard-success">').text(copy_str);
        success.prependTo(e.trigger).delay(1000).fadeOut();
    });
    clip.on('error', function(e) {
        // Safari doesn't support the execCommand (yet) but because clipboardjs
        // also uses Selection API, we can instruct users to just press the keyboard shortcut
        // See https://clipboardjs.com/#browser-support
		var copy_str = gettext("Press ⌘-C to copy");
        var success = $('<span class="clipboard-success">').text(copy_str);
        success.prependTo(e.trigger).delay(5000).fadeOut();
    });
});
