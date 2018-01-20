define([
    'jquery',
], function( $ ) {

    var ConsoleBlock = function(class_name) {
        this.console_blocks = $(class_name);
        this.init();
    };

    ConsoleBlock.prototype = {
        init: function(){
            var self = this;
            $(document).ready(function () {
                $(".c-tab-unix").on("click", function() {
                    $("section.c-content-unix").show();
                    $("section.c-content-win").hide();
                    $(".c-tab-unix").prop("checked", true);
                });
                $(".c-tab-win").on("click", function() {
                    $("section.c-content-win").show();
                    $("section.c-content-unix").hide();
                    $(".c-tab-win").prop("checked", true);
                });
            });
        }
    };

    // Export a single instance of our module:
    return new ConsoleBlock('.console-block');
});
