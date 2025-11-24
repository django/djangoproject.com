from django import template


class CachedLibrary(template.Library):
    def cached_context_simple_tag(self, name=None):
        """
        Wraps @register.simple_tag(takes_context=True) to cache the returned
        value inside the template's render_context during a single template
        render pass.

        This is useful when a tag may be rendered multiple times within the
        same template and with an expensive computation (e.g. due to database
        queries).
        """

        def decorator(func):
            tag_name = name or func.__name__

            @self.simple_tag(takes_context=True, name=tag_name)
            def wrapper(context, *args, **kwargs):
                render_context = getattr(context, "render_context", None)
                cache_key = f"{tag_name}_cached_value"

                if render_context is not None and cache_key in render_context:
                    return render_context[cache_key]

                result = func(context, *args, **kwargs)

                if render_context is not None:
                    render_context[cache_key] = result

                return result

            return wrapper

        return decorator
