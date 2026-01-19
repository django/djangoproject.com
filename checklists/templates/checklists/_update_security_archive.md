{% load checklist_extras %}
- [ ] In the `main` branch, add security patches entry to archive and backport

    - `git checkout main`

    - Edit existing file `docs/releases/security.txt`
```
{% include 'checklists/release_security_archive.rst' %}
```

    - In an environment with django branch and docs dependencies installed:
        - `cd docs && make html check`

    - Check local docs:
        - `firefox docs/_build/html/releases/security.html`

    - Add the changes and commit
        - `git commit -a -m 'Added {{ cves|enumerate_cves }} to security archive.'`

    - Backport security archive update to all branches!
        {% for release in instance.affected_releases %}
        - `git checkout {{ release.stable_branch }} && backport.sh {HASH}`
        {% endfor %}
