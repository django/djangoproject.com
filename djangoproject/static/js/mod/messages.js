define([
    'jquery' //requires jquery
], function( $ ) {
    $('.messages li').on('click', '.close', function() {
        $(this).parents('.messages > li').fadeOut();
    });
});


