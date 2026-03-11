{% load checklist_extras %}
- [ ] Change version in `django/__init__.py` and maybe trove classifier:
    - `VERSION = {{ release.version_tuple|format_version_tuple|safe }}`{% if not instance.is_security_release %}
    - Ensure the "Development Status" trove classifier in `pyproject.toml` is: `{{ instance.trove_classifier }}`{% endif %}
    - `git commit -a -m '{{ release.commit_prefix }} Bumped version for {{ release.version_verbose }} release.'`
    - e.g. https://github.com/django/django/commit/25fec8940b24107e21314ab6616e18ce8dec1c1c

- [ ] Enable the venv dedicated to build releases:
    - `source ~/.venvs/djangorelease/bin/activate`

- [ ] Run release script from `scripts` folder:
    - `PGP_KEY_ID={{ releaser.key_id }} PGP_KEY_URL={{ releaser.key_url }} DEST_FOLDER=../releases scripts/do_django_release.py`

- [ ] Execute ALL commands except for those to upload to Django admin and upload to PyPI, including:
    - `gpg --clearsign --digest-algo SHA256 <path-to-checksums-folder>/Django-{{ release.version }}.checksum.txt`
    - `git tag --sign --message="Tag {{ release.version }}" {{ release.version }}`
    - `git tag --verify {{ release.version }}`{% if not release.is_pre_release %}

- [ ] BUMP **MINOR VERSION** in `django/__init__.py`
    - `VERSION = {{ release|next_version_tuple|format_version_tuple|safe }}`
    - `git commit -a -m '{{ release.commit_prefix }} Post-release version bump.'`{% endif %}
