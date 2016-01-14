define('dashboard/detail', ['jquery', 'jquery.flot', 'dashboard/utils'], function ($, plot, utils) {
    $(function () {
        var element = $("#graph");
        var url = element.data('path') + element.data('metric') + ".json?days=365";
        var hover = {
            show: function (x, y, message) {
                $('<div id="hover">').html(message)
                                     .css({top: y, left: x})
                                     .appendTo('body')
                                     .show();
            },
            hide: function () {
                $("#hover").remove();
            }
        };

        $.getJSON(url, function (response) {
            for (var i = 0; i < response.data.length; i++) {
                response.data[i][0] = response.data[i][0] * 1000;
            }
            var options = {
                xaxis: {
                    mode: "time",
                    tickColor: "rgba(0,0,0,0)",
                    minTickSize: [1, "day"]
                },
                yaxis: {min: 0, ticks: 4},
                grid: {borderWidth: 0, hoverable: true, color: "#0C3C26"},
                colors: ["#0C4B33"]
            };
            if (response.period == "daily") {
                options.bars = {
                    show: true,
                    barWidth: 22 * 60 * 60 * 1000,
                    align: "center"
                };
            } else if (response.period == 'weekly') {
                options.bars = {
                    show: true,
                    barWidth: 22 * 60 * 60 * 7 * 1000,
                    align: "center"
                };
            }
            var plot = $.plot(element, [response.data], options);

            var format_message = function (timestamp, measurement) {
                var unit = measurement == 1 ? response.unit : response.unit_plural;
                return utils.formatTimestamp(timestamp, response.period) + '<br>' + measurement + ' ' + unit;
            };

            var previousPoint = null;
            element.bind("plothover", function (event, pos, item) {
                if (item) {
                    if (previousPoint != item.dataIndex) {
                        previousPoint = item.dataIndex;
                        hover.hide();
                        var x, y;
                        var message = format_message.apply(null, item.datapoint);
                        if (response.period == 'instant') {
                            x = item.pageX + 10;
                            y = item.pageY + 10;
                        } else {
                            // I'd like this hover to be centered over the bar. This
                            // simple math sorta works, but it assumes a *lot* about
                            // the plot and basically won't scale. Grr.
                            x = item.pageX - 40;
                            y = item.pageY - 50;
                        }
                        hover.show(x, y, message);
                    }
                } else {
                    hover.hide();
                    previousPoint = null;
                }
            });
        });
    });
});
