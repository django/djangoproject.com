from django.utils.regex_helper import _lazy_re_compile

version_component_re = _lazy_re_compile(r"(\d+|[a-z]+|\.)")


def get_loose_version_tuple(version):
    """
    Return a tuple of version numbers (e.g. (1, 2, 3, 'b', 2)) from the version
    string (e.g. '1.2.3b2').
    """
    version_numbers = []
    for item in version_component_re.split(version):
        if item and item != ".":
            try:
                component = int(item)
            except ValueError:
                component = item
            version_numbers.append(component)
    return tuple(version_numbers)
