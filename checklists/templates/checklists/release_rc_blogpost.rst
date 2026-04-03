Django {{ final_version }} release candidate 1 is now available. It represents
the final opportunity for you to try out the version that
`{{ instance.feature_release.tagline }}`__,
before Django {{ final_version }} final is released.

__ https://docs.djangoproject.com/en/dev/releases/{{ final_version }}/

The release candidate stage marks the string freeze and the call for
translators `to submit translations
<https://docs.djangoproject.com/en/dev/internals/contributing/localizing/#translations>`_.
Provided no major bugs are discovered that can't be solved in the next two
weeks, Django {{ final_version }} will be released on or around
{{ instance.feature_release.when|date:"F j" }}. Any  delays will be communicated
on the `on the Django forum <{{ instance.feature_release.forum_post }}>`_.

Please use this opportunity to help find and fix bugs (which should be reported
to `the issue tracker <https://code.djangoproject.com/newticket>`_), you can
grab a copy of the release candidate package from
`our downloads page <https://www.djangoproject.com/download/>`_ or on PyPI.

{% include "checklists/_releaser_info.rst" %}
