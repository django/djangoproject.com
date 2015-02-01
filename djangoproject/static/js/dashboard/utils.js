define('dashboard/utils', ['jquery'], function ($) {
	return {
		formatTimestamp: function formatTimestamp(timestamp, period) {
			var d = new Date(timestamp);
			if (period == 'instant') {
				return $.plot.formatDate(d, "%b %d, %h:%M %p");
			} else if (period == 'daily') {
				return $.plot.formatDate(d, "%b %d");
			} else if (period == 'weekly') {
				// A bit more complicated than the above: the timestamp is in the
				// middle of the week, so we have to bracket the date. This is
				// something of a fudge here, but it works well enough.
				var start = new Date(d.getTime() - (3 * 24 * 60 * 60 * 1000));
				var end = new Date(d.getTime() + (3 * 24 * 60 * 60 * 1000));
				return $.plot.formatDate(start, "%b %d") + ' - ' + $.plot.formatDate(end, "%b %d");
			}
		},
		convertSecondsToMilliseconds: function convertSecondsToMilliseconds(data) {
			for (var i = 0; i < data.length; i++) {
				data[i][0] = data[i][0] * 1000;
			}
			return data;
		}
	};
});
