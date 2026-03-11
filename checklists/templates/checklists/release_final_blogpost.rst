The Django team is happy to announce the release of Django {{ version }}.

`The release notes <https://docs.djangoproject.com/en/{{ version }}/releases/{{ version }}/>`_
showcase {{ tagline }}. A few highlights are:

{{ highlights|default:"* Add highlights in the admin." }}

You can get Django {{ version }} from `our downloads page
<https://www.djangoproject.com/download/>`_ or from `the Python Package Index
<https://pypi.python.org/pypi/Django/{{ version }}>`_.

{% include "checklists/_releaser_info.rst" %}
{% if instance.eom_release %}
With the release of Django {{ version }}, Django {{ instance.eom_release.feature_version}}
has reached the end of mainstream support. The final minor bug fix release,
`{{ instance.eom_release.version }}
<https://docs.djangoproject.com/en/stable/releases/{{ instance.eom_release.version }}/>`_,
was issued on {{ instance.eom_release.date }}. Django {{ instance.eom_release.feature_version }}
will receive security and data loss fixes until {{ instance.eom_release.feature_release.eol_date|date:"F, Y" }}.
All users are encouraged to upgrade before then to continue receiving fixes for
security issues.
{% endif %}
{% if instance.eol_release %}
Django {{ instance.eol_release.feature_version }} has reached the end of extended support.
The final security release, `{{ instance.eol_release.version }}
<https://docs.djangoproject.com/en/stable/releases/{{ instance.eol_release.version }}/>`_,
was issued on {{ instance.eol_release.date }}. All Django {{ instance.eol_release.feature_version }}
users are encouraged to `upgrade
<https://docs.djangoproject.com/en/dev/howto/upgrade-version/>`_ to a supported
Django version.
{% endif %}
See the `downloads page
<https://www.djangoproject.com/download/#supported-versions>`_ for a table of
supported versions and the future release schedule.
