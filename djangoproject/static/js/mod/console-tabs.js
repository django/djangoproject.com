define([
    'jquery',
], function( $ ) {
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
});
