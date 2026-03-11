{% load checklist_extras %}
In accordance with `our security release policy
<https://docs.djangoproject.com/en/dev/internals/security/>`_, the Django team
is issuing releases for
{{ versions|format_versions_for_blogpost|safe|wordwrap:79 }}.
These releases address the security issues detailed below. We encourage all
users of Django to upgrade as soon as possible.
{% for cve in cves %}
{{ cve.headline_for_blogpost|rst_backticks|rst_underline_for_headline:'=' }}

{{ cve.blogdescription|safe|default:cve.description }}
{% if cve.reporter %}
Thanks to {{ cve.reporter }} for the report.
{% endif %}
This issue has severity "{{ cve.severity }}" according to the Django security policy.
{% endfor %}

Affected supported versions
===========================
{% for branch in instance.affected_branches %}
* Django {{ branch }}{% endfor %}

Resolution
==========

Patches to resolve the issue have been applied to Django's
{{ instance.affected_branches|enumerate_items }} branches.
The patches may be obtained from the following changesets.
{% for cve in cves %}
{{ cve.headline_for_blogpost|rst_backticks|rst_underline_for_headline:'-' }}
{% for branch, hash in cve.hashes_by_branch %}
* On the `{{ branch }} branch <https://github.com/django/django/commit/{{ hash }}>`__{% endfor %}
{% endfor %}

The following releases have been issued
=======================================
{% for version in versions %}
* Django {{ version }} (`download Django {{ version }}
  <https://www.djangoproject.com/download/{{ version }}/tarball/>`_ |
  `{{ version }} checksums
  <https://www.djangoproject.com/download/{{ version }}/checksum/>`_){% endfor %}

{% include "checklists/_releaser_info.rst" %}

General notes regarding security reporting
==========================================

As always, we ask that potential security issues be reported via private email
to ``security@djangoproject.com``, and not via Django's Trac instance, nor via
the Django Forum. Please see `our security policies
<https://www.djangoproject.com/security/>`_ for further information.
