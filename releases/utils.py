"""
Parsing and formatting of Django release numbers, in both the A.B[.C] and the
calendar (YYYY[.N]) schemes.
"""

from django.utils.regex_helper import _lazy_re_compile

version_component_re = _lazy_re_compile(r"(\d+|[a-z]+|\.)")

# Feature releases from this year on are calendar versioned, YYYY[.N], where N
# is the patch number. Earlier releases use A.B[.C]. See DEP 20.
FIRST_CALENDAR_VERSION_YEAR = 2028

STATUS_ALIASES = {"a": "alpha", "b": "beta", "c": "rc"}


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


def get_version_tuple(version):
    """Return a tuple in the format of django.VERSION from a version string.

    Examples: (5, 2, 1, 'final', 0) for "5.2.1" and (2028, 0, 0, 'alpha', 1)
    for "2028a1".
    """
    version = version.replace("-", "").replace("_", "")
    components = list(get_loose_version_tuple(version))
    # The numeric components come first, optionally followed by the release
    # status and its iteration, as in "5.2a1" or "2028rc1".
    numbers = []
    for component in components:
        if not isinstance(component, int):
            break
        numbers.append(component)
    numbers_len = len(numbers)
    status, *iteration = components[numbers_len:] or ["final"]
    numbers += [0] * (3 - len(numbers))
    return (*numbers, STATUS_ALIASES.get(status, status), *(iteration or [0]))


def is_calendar_version(version):
    """Return True if the version tuple uses calendar versioning (YYYY[.N])."""
    return version[0] >= FIRST_CALENDAR_VERSION_YEAR


def get_main_version(version):
    """Return the main version (A.B[.C] or YYYY[.N]) from a version tuple."""
    # The patch number is the last component of the main version and is
    # omitted when zero. It's the second component for calendar versions
    # (YYYY[.N]) and the third one for the earlier scheme (A.B[.C]).
    patch_index = 1 if is_calendar_version(version) else 2
    parts = patch_index if version[patch_index] == 0 else patch_index + 1
    return ".".join(str(x) for x in version[:parts])


def get_feature_version(version):
    """Return the feature release version for a given version string."""
    components = get_loose_version_tuple(version)
    if is_calendar_version(components):
        return str(components[0])
    return ".".join(str(component) for component in components[:2])
