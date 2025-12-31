from django import template


class CachedLibrary(template.Library):
    def cached_context_inclusion_tag(self, template_name, *, name=None):
        """
        Wraps @register.inclusion_tag(template_name, takes_context=True) to
        automatically cache the returned context dictionary inside the
        template's render_context for the duration of a single render pass.

        This is useful when a tag may be rendered multiple times within the
        same template and computing its context is expensive (e.g. due to
        database queries).
        """

        def decorator(func):
            tag_name = name or func.__name__

            @self.inclusion_tag(template_name, takes_context=True, name=tag_name)
            def wrapper(context, *args, **kwargs):
                render_context = getattr(context, "render_context", None)
                cache_key = f"{tag_name}_cached_context"

                if render_context is not None and cache_key in render_context:
                    return render_context[cache_key]

                result = func(context, *args, **kwargs)

                if render_context is not None:
                    render_context[cache_key] = result

                return result

            return wrapper

        return decorator
