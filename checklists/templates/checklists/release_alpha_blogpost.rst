Django {{ final_version }} alpha 1 is now available. It represents the first
stage in the {{ final_version }} release cycle and is an opportunity to try out
the changes coming in Django {{ final_version }}.

Django {{ final_version }} {{ instance.feature_release.tagline }}, which you
can read about in `the in-development {{ final_version }} release notes
<https://docs.djangoproject.com/en/dev/releases/{{ final_version }}/>`_.

This alpha milestone marks the feature freeze. The `current release schedule
<https://www.djangoproject.com/download/{{ final_version }}/roadmap/>`_ calls
for a beta release in about a month and a release candidate roughly a month
after that. We'll only be able to keep this schedule with early and frequent
testing from the community. Updates on the release schedule are available `on
the Django forum <{{ instance.feature_release.forum_post }}>`_.

As with all alpha and beta packages, this release is **not** for production
use. However, if you'd like to take some of the new features for a spin, or
help find and fix bugs (which should be reported to `the issue tracker
<https://code.djangoproject.com/newticket>`_), you can grab a copy of the alpha
package from `our downloads page <https://www.djangoproject.com/download/>`_ or
on PyPI.

{% include "checklists/_releaser_info.rst" %}
