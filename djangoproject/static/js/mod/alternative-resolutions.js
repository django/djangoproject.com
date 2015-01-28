define(['jquery', 'modernizr-retina-test'], function ($){
    if (Modernizr.hires) {
        $('img[data-src-2x]').each(function() {
            $this = $(this);
            $this.attr('src', $this.attr('data-src-2x'))
        });
    }
});
