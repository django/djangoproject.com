- [ ] Switch to the branch and update it:
    - `git checkout {% if release != "main" %}{{ release.stable_branch }}{% else %}main{% endif %} && git pull -v`
{% for cve in cves %}
- [ ] Apply patch for **{{ cve }}**
    - `git am path/to/patch/for/{{ release }}/000{{ forloop.counter }}-{{ cve }}.patch`
        - `git am --abort` to the rescue if there are issues
{% if release != "main" %}
    - [ ] **Amend** the commit message to add prefix, backport hash, and record resulting hash:
        - `git commit --amend && git show`
        - `{{ release.commit_prefix }}`
        - `Backport of {{ cve.commit_hash_main|default:"{HASH-FROM-MAIN}" }} from main.`
{% endif %}
    - [ ] **SAVE** resulting hash in the [security issue instance]({% url 'admin:'|add:app_label|add:'_securityissue_change' cve.id %})
          *{% if release != "main" %}(scroll down to inlines){% else %}(use the `Commit hash main` field){% endif %}*
{% endfor %}
