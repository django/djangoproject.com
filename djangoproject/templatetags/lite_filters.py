"""
Template filters for lite templates

These filters help extract CSS and JavaScript from flatpage content
to properly place them in the document head and footer sections.
"""

import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def extract_head_tags(value):
    """
    Extract <link> and <style> tags from HTML content for placement in <head>

    Usage: {{ flatpage.content|extract_head_tags }}
    """
    if not value:
        return ""

    # Pattern to match <link> tags (CSS stylesheets, fonts, etc.)
    link_pattern = r"<link[^>]*?>"

    # Pattern to match <style> tags with their content
    style_pattern = r"<style[^>]*?>.*?</style>"

    # Find all matches
    links = re.findall(link_pattern, value, re.IGNORECASE | re.DOTALL)
    styles = re.findall(style_pattern, value, re.IGNORECASE | re.DOTALL)

    # Combine and return
    head_content = "\n".join(links + styles)
    return mark_safe(head_content)


@register.filter
def remove_head_tags(value):
    """
    Remove <link> and <style> tags from HTML content to avoid duplication

    Usage: {{ flatpage.content|remove_head_tags }}
    """
    if not value:
        return ""

    # Remove <link> tags
    value = re.sub(r"<link[^>]*?>", "", value, flags=re.IGNORECASE | re.DOTALL)

    # Remove <style> tags and their content
    value = re.sub(
        r"<style[^>]*?>.*?</style>", "", value, flags=re.IGNORECASE | re.DOTALL
    )

    return mark_safe(value)


@register.filter
def extract_script_tags(value):
    """
    Extract <script> tags from HTML content for placement before </body>

    Usage: {{ flatpage.content|extract_script_tags }}
    """
    if not value:
        return ""

    # Pattern to match <script> tags with their content
    script_pattern = r"<script[^>]*?>.*?</script>"

    # Find all matches
    scripts = re.findall(script_pattern, value, re.IGNORECASE | re.DOTALL)

    return mark_safe("\n".join(scripts))


@register.filter
def remove_script_tags(value):
    """
    Remove <script> tags from HTML content to avoid duplication

    Usage: {{ flatpage.content|remove_script_tags }}
    """
    if not value:
        return ""

    # Remove <script> tags and their content
    value = re.sub(
        r"<script[^>]*?>.*?</script>", "", value, flags=re.IGNORECASE | re.DOTALL
    )

    return mark_safe(value)


@register.filter
def clean_content_for_lite(value):
    """
    Combined filter to clean flatpage content for lite templates
    Removes both head tags and script tags

    Usage: {{ flatpage.content|clean_content_for_lite }}
    """
    if not value:
        return ""

    # Remove head tags first, then script tags
    value = remove_head_tags(value)
    value = remove_script_tags(value)

    return value
