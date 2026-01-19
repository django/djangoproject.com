    - Visit https://cveform.mitre.org/ and fill out the web form as follows for {{ cve }}:
        - _Select request type_: `Notify CVE about a publication`
        - _Enter your e-mail address_: `security@djangoproject.com`
        - _Enter a PGP Key_: _blank_
        - _Link to the advisory_: `{{ instance.blogpost_link }}`
        - _CVE IDs of vulnerabilities to be published_: `{{ cve }}`
        - _Date published_: `{{ instance.when.date|date:"m/d/Y" }}`
        - _Additional information and CVE ID description updates_:
```
Please publish the following CVE record for {{ cve }}:
{{ cve.cve_minified_json|safe }}
```
