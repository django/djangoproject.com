{% load checklist_extras %}
- [ ] In the `main` branch, start release notes for the next version for the latest stable branch:

    - `git checkout main`{% with next_version=release|next_version %}

    - Edit existing file `docs/releases/index.txt`
        - Add an entry for: `{{ next_version }}`

    - Add new file `docs/releases/{{ next_version }}.txt`
        - Content for stub releases notes:
```
{{ next_version|stub_release_notes_title }}

*Expected {{ release.date|next_release_date|date:"F j, Y" }}*

Django {{ next_version }} fixes several bugs in {{ release.version }}.

Bugfixes
========

* ...

```

    - In an environment with django branch and docs dependencies installed:
        - `cd docs && make html check`

    - Check local docs:
        - `firefox docs/_build/html/releases/index.html`

    - Add the new file and commit
        - `git add docs/releases/{{ next_version }}.txt`
        - `git commit -a -m 'Added stub release notes for {{ next_version }}.'`

    - Backport stub release notes to latest stable branch!
        - `backport.sh {HASH}`{% endwith %}
