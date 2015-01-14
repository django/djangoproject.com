define('dashboard/index', ['jquery', 'jquery.flot', 'dashboard/dddash'], function ($, flot, dddash) {
    $(function () {
        $(".metric .sparkline").each(function (index, elem) {
            var e = $(elem);
            var valueElement = e.parent().find('.value a');
            var timestampElement = e.parent().find('.timestamp');
            var originalValue = valueElement.html();
            var green = '#93D7B7';

            var url = "/metric/" + e.data('metric') + ".json";
            $.getJSON(url, function (response) {
                response.data = dddash.convertSecondsToMilliseconds(response.data);
                $.plot(e, [response.data], {
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

                e.bind('plothover', function (event, pos, item) {
                    if (item) {
                        valueElement.html(item.datapoint[1]);
                        timestampElement.html(dddash.formatTimestamp(item.datapoint[0], response.period));
                    } else {
                        valueElement.html(originalValue);
                        timestampElement.html('&nbsp;');
                    }
                });
            });

            e.click(function () {
                window.location = "/metric/" + e.data('metric') + '/';
            })
        });
    });
});
