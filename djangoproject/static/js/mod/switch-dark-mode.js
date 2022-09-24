define([
    'jquery' //requires jquery
], function ($) {
	const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    function setTheme(mode) {
        if (mode !== "light" && mode !== "dark" && mode !== "auto") {
            console.error(`Got invalid theme mode: ${mode}. Resetting to auto.`);
            mode = "auto";
        }
        document.documentElement.dataset.theme = mode;
        localStorage.setItem("theme", mode);
    }

    function cycleTheme() {
        const currentTheme = localStorage.getItem("theme") || "auto";

        if (prefersDark) {
            // Auto (dark) -> Light -> Dark
            if (currentTheme === "auto") {
                setTheme("light");
            } else if (currentTheme === "light") {
                setTheme("dark");
            } else {
                setTheme("auto");
            }
        } else {
            // Auto (light) -> Dark -> Light
            if (currentTheme === "auto") {
                setTheme("dark");
            } else if (currentTheme === "dark") {
                setTheme("light");
            } else {
                setTheme("auto");
            }
        }

		setReleaseImgClass();
    }

    function initTheme() {
        // set theme defined in localStorage if there is one, or fallback to auto mode
        const currentTheme = localStorage.getItem("theme");
        currentTheme ? setTheme(currentTheme) : setTheme("auto");
		setReleaseImgClass();
    }

    function setupTheme() {
        // Attach event handlers for toggling themes
        const buttons = document.getElementsByClassName("theme-toggle");
        Array.from(buttons).forEach((btn) => {
            btn.addEventListener("click", cycleTheme);
        });
        initTheme();
		setReleaseImgClass();
    }

	function setReleaseImgClass() {
		// set class for the image about releases to invert color if needed
		const currentTheme = localStorage.getItem("theme") || "auto";
		const image = document.getElementsByClassName("img-release")[0];

		if(currentTheme == "auto" && prefersDark) {
			$(image).addClass('dark')
			$(image).removeClass('light')
		}
		if(currentTheme == "auto" && !prefersDark) {
			$(image).addClass('light')
			$(image).removeClass('dark')
		}
		if(currentTheme == "light") {
			$(image).addClass('light')
			$(image).removeClass('dark')
		}
		if(currentTheme == "dark") {
			$(image).addClass('dark')
			$(image).removeClass('light')
		}
	}



    $(document).on('ready', function () {
        setupTheme();
    });
})
