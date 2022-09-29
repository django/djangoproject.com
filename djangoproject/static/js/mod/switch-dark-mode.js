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
		// trim host to get base domain name for set in cookie domain name for subdomain access
		arrHost = window.location.hostname.split('.')
		prefix = arrHost.shift()
		host = arrHost.join('.')
		setCookie('theme', mode, host)
    }

    function cycleTheme() {
        const currentTheme = getCookie("theme") || "auto";

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
        const currentTheme = getCookie("theme");
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

	function setCookie(cname, cvalue, domain, exdays) {
		const d = new Date();
		d.setTime(d.getTime() + (exdays*24*60*60*1000));
		let expires = "expires="+ d.toUTCString();
		document.cookie = `${cname}=${cvalue}; Domain=${domain}; ${expires};path=/`;
	}

	function getCookie(cname) {
		let name = cname + "=";
		let decodedCookie = decodeURIComponent(document.cookie);
		let ca = decodedCookie.split(';');
		for(let i = 0; i <ca.length; i++) {
		  let c = ca[i];
		  while (c.charAt(0) == ' ') {
			c = c.substring(1);
		  }
		  if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		  }
		}
		return "";
	  }



    $(document).on('ready', function () {
        setupTheme();
    });
})
