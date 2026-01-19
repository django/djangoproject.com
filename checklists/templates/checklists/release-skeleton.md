{% load checklist_extras %}
# Django {{ release.version_verbose }} {{ title }} - {{ when|date }}

{% if release.status == "a" %}
## One or Two months before Feature Freeze
- [ ] Create a new topic in the `Prereleases` category in the Discourse forum
    - https://forum.djangoproject.com/c/announcements/prereleases/32
    - Title: `Django {{ release.feature_version }} release - timeline and next steps`
    - Tags: {% for tag in instance.tags %}`{{ tag }}`{% if not forloop.last %}, {% endif %}{% endfor %}
    - Content:
```
:mega: It's time to prepare for Django {{ release.feature_version }}!

Hello!

It's time to look ahead to our next feature release: Django {{ release.feature_version }}.
You can find the timeline in the [roadmap page](https://www.djangoproject.com/download/{{ release.feature_version }}/roadmap/).

If you are working on something that is nearly ready, feel free to share it here. We are happy to support progress where we can.
Please keep in mind that not every in-progress feature will make it into this release, and anything that does not land will be reconsidered for future feature releases.

At this point, most of the larger features planned for {{ release.feature_version }} are already underway, but there is still room for smaller or well-scoped contributions. We would love to hear what you are working on.
```
{% endif %}

## A few days before any release

- [ ] Resolve release blockers
{% if instance.forum_post %}
- [ ] Update [forum post]({{ instance.forum_post }}) with any relevant news
{% endif %}
{% include 'checklists/_write_blogpost.md' with final_version=release.feature_version %}
{% if release.is_dot_zero %}
- [ ] Update translations from Transifex
    - See [how to release Django docs](https://docs.djangoproject.com/en/dev/internals/howto-release-django/#a-few-days-before-any-release)
      and [example commit in stable branch](https://github.com/django/django/commit/cc31b389a11559396fc039511c0dc567d9ade469)
    - Forwardport the commit from the stable branch into `main` ([example commit](https://github.com/django/django/commit/cb27e5b9c0703fb0edd70b2138e3e53a78c9551d))

- [ ] Create a new branch from the current stable branch in the [django-docs-translations repository](https://github.com/django/django-docs-translations):
    - `git checkout -b {{ release.stable_branch }} origin/{{ instance.eom_release.stable_branch }}`
    - `git push origin {{ release.stable_branch }}:{{ release.stable_branch }}`
{% elif release.status == "a" %}
## Feature Freeze Day
{% include 'checklists/_feature_freeze.md' with final_version=release.feature_version %}
{% endif %}

## Release Day

- [ ] Polish and  make cosmetic edits to release notes on `main` and backport
    {% if not release.is_pre_release %}
    - Remove the `Expected` prefix and update the release date if necessary
    {% endif %}
    {% if release.is_dot_zero %}- Remove the `UNDER DEVELOPMENT` header at the top of the release notes:
        - e.g. https://github.com/django/django/commit/1994a2643881a9e3f9fa8d3e0794c1a9933a1831{% endif %}

- [ ] Check Jenkins (https://djangoci.com/job/django-{{ release.feature_version }}/) is green for the version(s) you're putting out.
    - You probably shouldn't issue a release until it's green.

- [ ] A release always begins from a release branch, so you should make sure you're on the up-to-date **stable branch**
    - `git checkout {{ release.stable_branch }} && git pull -v`

{% if not release.is_pre_release %}{% include 'checklists/_update_man_page.md' %}{% endif %}

### Build artifacts
{% include 'checklists/_build_release_binaries.md' %}

### Publish artifacts

{% include 'checklists/_make_release_public.md' %}

### Final tasks

{% if not release.is_pre_release %}{% include "checklists/_stub_release_notes.md" %}{% endif %}

{% include "checklists/_push_changes_and_announce.md" %}

{% if release.status == "a" %}
- [ ] Add the feature release in [Trac's versions list](https://code.djangoproject.com/admin/ticket/versions).
{% endif %}
{% if release.is_dot_zero %}
- [ ] Update the metadata for the docs in https://www.djangoproject.com/admin/docs/documentrelease/:
    - Set `is_default` flag to `True` in the `DocumentRelease` English entry for this release (this will automatically flip all the others to `False`).
    - Create new `DocumentRelease` objects for each language that has an entry for the previous release.

- [ ] Update djangoproject.com:
    - [ ] Extend [robots.docs.txt](https://github.com/django/djangoproject.com/blob/main/djangoproject/static/robots.docs.txt) file
        - Add the result from running in the following using the [django-docs-translations repository](https://github.com/django/django-docs-translations)
        - `git checkout {{ release.stable_branch }} && git pull -v`
        - `python manage_translations.py robots_txt`
        - e.g. https://github.com/django/djangoproject.com/pull/1445
    - [ ] Advance the version in the download page's tables
        - e.g. https://github.com/django/djangoproject.com/commit/942a242df7b63f579ca995132bbf0ae0bd3dbbc2

- [ ] Update the current stable branch and remove the pre-release branch in the
      [Django release process](https://code.djangoproject.com/#Djangoreleaseprocess) on Trac

- [ ] Update the `default_version` setting in the code.djangoproject.com's `trac.ini` file
    - e.g. https://github.com/django/code.djangoproject.com/pull/268
{% elif release.is_pre_release %}
- [ ] Update the translation catalogs:
    - Make a new branch from the recently released stable branch:
        - `git checkout {{ release.stable_branch }} && git pull -v`
        - `git checkout -b update-translations-catalog-{{ release.feature_version }}.x`

    - Ensure that the release's dedicated virtual environment is enabled and run the following:
        - `cd django`
        - `django-admin makemessages -l en --domain=djangojs --domain=django`

    - Review the diff before pushing and avoid committing changes to the `.po` files without any new translations.
        - e.g. https://github.com/django/django/commit/d2b1ec551567c208abfdd21b27ff6d08ae1a6371.

    - Make a pull request against the corresponding stable branch and merge once approved.

    - Forward port the updated source translations to the `main` branch.
        - e.g. https://github.com/django/django/commit/aed303aff57ac990894b6354af001b0e8ea55f71.
{% endif %}
{% if release.status == "c" %}
- [ ] Create a new topic in the `Internationalization` category in the Discourse forum
    - https://forum.djangoproject.com/c/internals/i18n/14
    - Title: `Django {{ release.feature_version }} string freeze is in effect, translations needed!`
    - Tags: {% for tag in instance.tags %}`{{ tag }}`{% if not forloop.last %}, {% endif %}{% endfor %}
    - e.g. https://forum.djangoproject.com/t/django-5-0-string-freeze-is-in-effect-translations-needed/25511
    - Content:
```
Hello Translators!

Django {{ release.version_verbose }} was [released today]({{ instance.blogpost_link }}), establishing the string freeze for the {{ release.feature_version }} release.
This means that strings marked for translations will not change between now and the final release, scheduled for approximately two weeks from now.

It would be extremely helpful if you could ensure that the Django translations for the languages you contribute to are complete on [Transifex](https://explore.transifex.com/django/django/).
We will be fetching the available translations a few days before the final release.

For more information about Django translations, refer to the [Localizing docs](https://docs.djangoproject.com/en/stable/internals/contributing/localizing/).

Thank you very much for your help!
```
{% endif %}
