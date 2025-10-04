# Get Involved Page Implementation Plan

## Problem Statement

DSF members at DjangoCon Europe 2025 requested a dedicated "Calls to Action" page to centralize opportunities for supporting Django.

## Requirements

1. **Time-based opportunities** (elections, conferences, prizes)
2. **Evergreen opportunities** (donate, translate, code review)
3. **Easy to update** when new opportunities arise
4. **Shareable link** for promotion

## Implementation Approach

### Option 1: Static Page (Simplest)

Create a new template with hardcoded sections that can be updated via Git commits.

### Option 2: Dynamic Content Management (Recommended)

Create a Django model to manage calls-to-action with admin interface.

## Proposed Structure

```
/get-involved/
├── Time-Sensitive Opportunities
│   ├── Board Elections (if active)
│   ├── Steering Council Elections (if active)
│   ├── DjangoCon Proposals (if open)
│   └── Malcolm Prize (if accepting)
├── Ongoing Ways to Help
│   ├── Financial Support
│   ├── Code Contributions
│   ├── Documentation
│   ├── Translation
│   ├── Community Support
│   └── Code Review
└── Getting Started Guide
```

## Technical Implementation

### 1. Create Model (Optional - for dynamic content)

```python
# get_involved/models.py
class CallToAction(models.Model):
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent/Time-Sensitive'),
        ('high', 'High Priority'),
        ('normal', 'Ongoing'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    is_active = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True)  # For time-sensitive items
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', 'deadline', '-created_at']
```

### 2. Create URLs

```python
# djangoproject/urls.py
urlpatterns = [
    # ... existing patterns
    path('get-involved/', include('get_involved.urls')),
]

# get_involved/urls.py
urlpatterns = [
    path('', views.get_involved, name='get_involved'),
]
```

### 3. Create View

```python
# get_involved/views.py
def get_involved(request):
    # If using dynamic model:
    urgent_actions = CallToAction.objects.filter(
        is_active=True,
        priority='urgent'
    )
    ongoing_actions = CallToAction.objects.filter(
        is_active=True,
        priority__in=['high', 'normal']
    )

    return render(request, 'get_involved/index.html', {
        'urgent_actions': urgent_actions,
        'ongoing_actions': ongoing_actions,
    })
```

### 4. Create Template

```html
<!-- templates/get_involved/index.html -->
{% extends "base.html" %} {% block title %}Get Involved with Django{% endblock
%} {% block content %}
<h1>Get Involved with Django</h1>
<p class="lead">
    There are many ways to support the Django project and community. Whether you
    have 5 minutes or 5 hours, there's something you can do to help make Django
    better.
</p>

{% if urgent_actions %}
<section class="urgent-actions">
    <h2>⏰ Time-Sensitive Opportunities</h2>
    {% for action in urgent_actions %}
    <div class="action-card urgent">
        <h3>{{ action.title }}</h3>
        <p>{{ action.description }}</p>
        {% if action.deadline %}
        <p class="deadline">Deadline: {{ action.deadline|date:"F j, Y" }}</p>
        {% endif %}
        <a href="{{ action.link }}" class="cta">Learn More</a>
    </div>
    {% endfor %}
</section>
{% endif %}

<section class="ongoing-actions">
    <h2>🌟 Ongoing Ways to Help</h2>

    <div class="action-grid">
        <div class="action-card">
            <h3>💰 Financial Support</h3>
            <p>Help fund Django's development and infrastructure</p>
            <a href="{% url 'fundraising:index' %}" class="cta">Donate</a>
        </div>

        <div class="action-card">
            <h3>💻 Code Contributions</h3>
            <p>Fix bugs, add features, improve performance</p>
            <a
                href="https://docs.djangoproject.com/en/dev/internals/contributing/"
                class="cta"
                >Start Contributing</a
            >
        </div>

        <div class="action-card">
            <h3>📚 Documentation</h3>
            <p>Help make Django's docs even better</p>
            <a
                href="https://docs.djangoproject.com/en/dev/internals/contributing/writing-documentation/"
                class="cta"
                >Write Docs</a
            >
        </div>

        <div class="action-card">
            <h3>🌍 Translation</h3>
            <p>Translate Django into your language</p>
            <a
                href="https://docs.djangoproject.com/en/dev/internals/contributing/localizing/"
                class="cta"
                >Translate</a
            >
        </div>

        <div class="action-card">
            <h3>👥 Community Support</h3>
            <p>Help others in forums and chat</p>
            <a href="https://forum.djangoproject.com/" class="cta"
                >Join Forum</a
            >
        </div>

        <div class="action-card">
            <h3>🔍 Code Review</h3>
            <p>Review pull requests and help improve code quality</p>
            <a href="https://github.com/django/django/pulls" class="cta"
                >Review Code</a
            >
        </div>
    </div>
</section>

<section class="getting-started">
    <h2>🚀 New to Contributing?</h2>
    <p>
        Check out our
        <a href="https://docs.djangoproject.com/en/dev/internals/contributing/"
            >contribution guide</a
        >
        to get started.
    </p>
</section>
{% endblock %}
```

### 5. Add Styles

```scss
// djangoproject/scss/_get-involved.scss
.action-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.action-card {
    border: 1px solid var(--hairline-color);
    border-radius: 8px;
    padding: 20px;

    &.urgent {
        border-color: var(--warning);
        background: var(--warning-admonition-bg);
    }

    h3 {
        margin-top: 0;
        color: var(--primary);
    }

    .deadline {
        font-weight: bold;
        color: var(--warning-dark);
    }

    .cta {
        display: inline-block;
        margin-top: 10px;
        padding: 8px 16px;
        background: var(--primary);
        color: white;
        text-decoration: none;
        border-radius: 4px;

        &:hover {
            background: var(--primary-accent);
        }
    }
}
```

## Next Steps

1. **Create the app structure**
2. **Design the page layout**
3. **Add admin interface** (if using dynamic model)
4. **Add navigation links** from main site
5. **Set up periodic review process** to keep content current

## Benefits

- **Single source of truth** for getting involved
- **Easy to share** - one URL covers everything
- **Promotes time-sensitive opportunities**
- **Reduces barrier to entry** for new contributors
- **Maintains engagement** with evergreen content
