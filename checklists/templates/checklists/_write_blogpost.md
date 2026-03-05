- [ ] Create blog post:
    - Navigate to: https://www.djangoproject.com/admin/blog/entry/add/
    - Headline: `{{ instance.blogpost_title }}`
    - Slug: `{{ slug }}`
    - Format: reStructuredText
    - Summary: `{{ instance.blogpost_summary }}`
    - Author: `{{ instance.releaser.user.get_full_name }}`
    - Active: `False`
    - Body:
```
{% include instance.blogpost_template %}
```
