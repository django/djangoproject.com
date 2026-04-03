{% load checklist_extras %}
{% load tz %}
You're receiving this message because you are on the security prenotification
list for the Django web framework; information about this list can be found in
our security policy [1].

In accordance with that policy, a set of security releases will be issued on
{{ when|utc|date:"l, F j, Y" }} around {{ when|utc|date:"H:i" }} UTC. This
message contains descriptions of the issue(s), descriptions of the changes
which will be made to Django, and the patches which will be applied to Django.
{% for cve in cves %}
{{ cve.headline_for_blogpost|rst_underline_for_headline:'=' }}

{{ cve.blogdescription|safe }}
{% endfor %}
Affected supported versions
===========================
{% for branch in instance.affected_branches %}
* Django {{ branch }}{% endfor %}

Resolution
==========

Included with this email are patches implementing the changes described above
for each affected version of Django. On the release date, these patches will be
applied to the Django development repository and the following releases will be
issued along with disclosure of the issues:
{% for version in versions %}
* Django {{ version }}{% endfor %}

[1] https://www.djangoproject.com/security/
