define([
	'jquery' //requires jquery
], function ($) {

	$(document).on('ready', function () {
		const useDarkMode = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)");
		const theme = window.localStorage.getItem('dark-mode');

		// Toggles the "dark-mode" class based on if the media query matches or if theme exist
		function toggleDarkMode(state, theme) {
			if (theme != null) {
				if (theme == 'true') {
					$('html').addClass("dark-mode");
				} else {
					$('html').removeClass("dark-mode");
				}
				$('#toggle').attr('aria-checked', theme);

			} else {
				$('html').toggleClass("dark-mode", state);
				$('#toggle').attr('aria-checked', state);
			}
		}

		// Initial setting
		if (theme) {
			toggleDarkMode(theme, theme);
		} else {
			toggleDarkMode(useDarkMode.matches, null);
		}

		// Listen for changes in the system preferences
		$(useDarkMode).on('change', function (evt) { toggleDarkMode(evt.target.matches, theme) });

		// Toggles the "dark-mode" class on click
		$("#toggle").on("click", () => {
			$('html').toggleClass("dark-mode");
			const state = $('#toggle').attr('aria-checked');
			const newState = (state == 'true') ? false : true;
			$('#toggle').attr('aria-checked', newState);
			window.localStorage.setItem('dark-mode', newState);
		});
	});
})


