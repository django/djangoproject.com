$(() => {
  $('.metric .sparkline').each((index, elem) => {
    const element = $(elem);
    const valueElement = element.parent().find('.value a');
    const timestampElement = element.parent().find('.timestamp');
    const originalValue = valueElement.html();
    const green = '#93D7B7';

    const url = `${element.data('path') + element.data('metric')}.json`;
    $.getJSON(url, (response) => {
      response.data = convertSecondsToMilliseconds(response.data);
      $.plot(element, [response.data], {
        xaxis: { show: false, mode: 'time' },
        yaxis: { show: false, min: 0 },
        grid: { borderWidth: 0, hoverable: true },
        colors: [green],
        bars: {
          show: true,
          barWidth:
            response.period == 'daily'
              ? 24 * 60 * 60 * 1000
              : 24 * 60 * 60 * 7 * 1000,
          fillColor: green,
          lineWidth: 1,
          align: 'center',
        },
      });

      element.bind('plothover', (event, pos, item) => {
        if (item) {
          valueElement.html(item.datapoint[1]);
          timestampElement.html(
            formatTimestamp(item.datapoint[0], response.period),
          );
        } else {
          valueElement.html(originalValue);
          timestampElement.html('&nbsp;');
        }
      });
    });
  });
});
