- [ ] Push changes to relevant branches:
{% if not instance.is_pre_release %}
    - `git checkout main && git log`
    - `git push -v`{% endif %}
{% for release in instance.affected_releases %}
    - `git checkout {{ release.stable_branch }} && git log`
    - `git push -v`
{% endfor %}

- [ ] Push all the new tags at once
    - `git push --tags`

- [ ] Publish blogpost

- [ ] Email to `django-announce@googlegroups.com`
    - Title: `{{ instance.blogpost_title }}`
    - Body with short notice and link to blogpost for more details:
```
Details are available on the Django project weblog:
{{ instance.blogpost_link }}
```
{% if instance.is_pre_release %}
- [ ] Update the [pre-releases forum post]({{ instance.forum_post }}) with the release announcement
    - New reply with content:
```
## {{ instance.blogpost_title }}

:mega: Announcement: {{ instance.blogpost_link }}

:tada: Release notes:

  * https://docs.djangoproject.com/en/dev/releases/{{ instance.feature_release.version }}
```
{% else %}
- [ ] Create a new topic in the `Releases` category in the Discourse forum
    - https://forum.djangoproject.com/c/announcements/releases/31
    - Title: `{{ instance.blogpost_title }}`
    - Tags: {% for tag in instance.tags %}`{{ tag }}`{% if not forloop.last %}, {% endif %}{% endfor %}
    - Content:
```
:mega: Announcement: {{ instance.blogpost_link }}

:tada: Release notes:
{% for version in instance.versions %}
 * https://docs.djangoproject.com/en/stable/releases/{{ version }}{% endfor %}
```
{% endif %}
