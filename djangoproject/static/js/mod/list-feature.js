define(['jquery'], function ($) {
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) {
                return;
            }

            $(entry.target).addClass('inview');

            observer.unobserve(entry.target);
        });

    }, { threshold: 1.0 });

    $('.list-features').find('i').each(function () {
        observer.observe(this);
    });
});
