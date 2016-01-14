define('dashboard/index', ['jquery', 'jquery.flot', 'dashboard/utils'], function ($, flot, utils) {
    $(function () {
        $(".metric .sparkline").each(function (index, elem) {
            var element = $(elem);
            var valueElement = element.parent().find('.value a');
            var timestampElement = element.parent().find('.timestamp');
            var originalValue = valueElement.html();
            var green = '#93D7B7';

            var url = element.data('path') + element.data('metric') + ".json";
            $.getJSON(url, function (response) {
                response.data = utils.convertSecondsToMilliseconds(response.data);
                $.plot(element, [response.data], {
                    xaxis: {show: false, mode: "time"},
                    yaxis: {show: false, min: 0},
                    grid: {borderWidth: 0, hoverable: true},
                    colors: [green],
                    bars: {
                        show: true,
                        barWidth: (response.period == 'daily' ? 24 * 60 * 60 * 1000 : 24 * 60 * 60 * 7 * 1000),
                        fillColor: green,
                        lineWidth: 1,
                        align: "center"
                    }
                });

                element.bind('plothover', function (event, pos, item) {
                    if (item) {
                        valueElement.html(item.datapoint[1]);
                        timestampElement.html(
                            utils.formatTimestamp(
                                item.datapoint[0],
                                response.period
                            )
                        );
                    } else {
                        valueElement.html(originalValue);
                        timestampElement.html('&nbsp;');
                    }
                });
            });
        });
    });
});
