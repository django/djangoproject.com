- [ ] Add (or edit if existing) the the [release entry in the admin](https://www.djangoproject.com/admin/releases/release?version={{ release }}):
    - Version: {{ release }}
    - Is active: False
    - LTS: {{ release.is_lts }}
    - Release date: {{ release.date.isoformat }}
    - End of life date: _blank_
    - Upload artifacts (tarball, wheel, .asc signed checksum)
    - Save
    - Check at: https://www.djangoproject.com/admin/releases/release/{{ release }}/change/

- [ ] Test the release locally with script from `scripts` folder:
    - `VERSION={{ release }} scripts/test_new_version.sh`

- [ ] Confirm the release signature with script from `scripts` folder:
    - `VERSION={{ release }} scripts/confirm_release.sh`

- [ ] Upload to PyPI with Twine (use commands printed by release script)
    - `cd ../releases/{{ release }}`
    - `twine upload --repository django dist/*`
    - https://pypi.org/project/Django/{{ release }}/

- [ ] Mark the release as "active" in
  https://www.djangoproject.com/admin/releases/release/{{ release }}/change/
