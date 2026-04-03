{% load checklist_extras %}
- [ ] Create a new PR targeting the `main` branch with 3 commits:
    - PR title: `Pre-edits for {{ version }}.`
        - e.g. https://github.com/django/django/pull/19049
        - e.g. https://github.com/django/django/pull/17276
    - `git checkout main && git pull -v`
    - `git checkout -b feature-freeze-{{ final_version }}`

{% include 'checklists/_update_man_page.md' %}

- [ ] Remove empty sections from the release notes:
    - `git commit -a -m 'Removed empty sections from {{ final_version }} release notes.'`

- [ ] Build the release notes locally and review for flow/grammar fixes and check links:
    - `cd docs`
    - `make html && make check && make linkcheck`
    - `git commit -a -m 'Made cosmetic edits to docs/releases/{{ final_version }}.txt.'`

- [ ] Get reviews and merge the pre-edits branch into `main`.

- [ ] Update `upstream/main` and create a new stable branch from it:
    - `git fetch --all --prune`
    - `git checkout -b {{ release.stable_branch }} upstream/main`
    - `git push upstream -u {{ instance.release.stable_branch }}:{{ instance.release.stable_branch }}`
{% with next_version=instance.feature_release.release|next_feature_version prereleases="1234"|make_list %}
- [ ] Update `django_next_version` in `docs/conf.py` on the new stable branch:
    - `django_next_version = '{{ next_version }}'`
    - `git commit -a -m '{{ release.commit_prefix }} Bumped django_next_version in docs config.'`

- [ ] Create inactive `Release` objects for {{ next_version }} in
      https://www.djangoproject.com/admin/releases/release/add/:
    {% for i in prereleases %}
    - Version: {{ next_version }}{% cycle 'a1' 'b1' 'rc1' '' %}
        - Is active: False
        - Mark LTS if applicable
        - Set scheduled release date
    {% endfor %}
    - Check the generated roadmap at https://www.djangoproject.com/download/{{ next_version }}/roadmap/.
{% endwith %}
- [ ] Create a `DocumentRelease` object in the admin for English for the new release:
    - Navigate to: https://www.djangoproject.com/admin/docs/documentrelease/add/
    - Steps:
        1. Select the `Release` object created above.
        2. Choose `English` as the language.
        3. Leave `Default` unchecked.
        4. Save.

- [ ] Add the new branch/version to Read the Docs:
  (https://app.readthedocs.org/dashboard/django/version/create/). Search for
  version `stable-{{ final_version }}.x`, add an alias/slug for it named
  `{{ final_version }}.x`, and make it active.
    - more info: https://github.com/readthedocs/readthedocs.org/issues/12483

- [ ] Request the new classifier on PyPI by making a PR:
    - `Framework :: Django :: {{ final_version }}`
    - e.g. https://github.com/pypa/trove-classifiers/pulls?q=is%3Apr+django+trove+classifier

- [ ] Edit the [Django release process on Trac](https://code.djangoproject.com/#Djangoreleaseprocess):
    - Update the current branch under active development
    - Add the pre-release branch

- [ ] Update `docs/fixtures/doc_releases.json` and
      `releases/fixtures/doc_releases.json` for djangoproject.com:
    - `python manage_translations.py export_json doc_releases.json`
    - e.g. https://github.com/django/djangoproject.com/pull/2209
