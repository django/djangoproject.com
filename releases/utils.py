"""
Parsing and formatting of Django release numbers, in both the A.B[.C] and the
calendar (YYYY[.N]) schemes.

Parts of this module duplicate django.utils.version, because the site runs the
latest *released* Django, and DEP 20 support landed in Django 6.2. On 6.1,
get_complete_version() asserts a five component tuple, so the four component
shape of a calendar version raises AssertionError, and get_main_version()
renders (2028, 0, 0, "final", 0) as "2028.0" rather than the "2028" we publish.

Django 6.2: when the site upgrades, drop the duplication as follows. Each site
is marked with a "Django 6.2:" comment, so `grep -rn "Django 6.2:"` lists them.

* get_main_version() -> django.utils.version.get_main_version(), which from 6.2
  reads the numbers as version[:-2] and so serves both schemes.
* get_django_version_tuple() and Release.django_version_tuple ->
  django.utils.version.VersionTuple, whose .feature and .patch give the same
  answers under both schemes.
What stays: is_calendar_version() and the year it compares against, because a
version *string* never says which scheme it belongs to, and a VersionTuple can
only be built once that is known; get_version_tuple() (core's returns only the
leading numbers, and we need the status and iteration); get_feature_version()
(core's get_docs_version() answers "dev" for pre-releases); and the release
process arithmetic in get_next_feature_version() and get_next_patch_version(),
which core has no equivalent for.
"""

from django.utils.regex_helper import _lazy_re_compile

# Copied verbatim from django.utils.version, where it is undocumented.
version_component_re = _lazy_re_compile(r"(\d+|[a-z]+|\.)")

# Feature releases from this year on are calendar versioned, YYYY[.N], where N
# is the patch number. Earlier releases use A.B[.C]. See DEP 20.
FIRST_CALENDAR_VERSION_YEAR = 2028

# The last feature release using the A.B scheme, succeeded by the first
# calendar version rather than by 7.0. See DEP 20.
LAST_NON_CALENDAR_FEATURE_VERSION = (6, 2)

STATUS_ALIASES = {"a": "alpha", "b": "beta", "c": "rc"}


def get_loose_version_tuple(version):
    """
    Return a tuple of version numbers (e.g. (1, 2, 3, 'b', 2)) from the version
    string (e.g. '1.2.3b2').

    Adapted from django.utils.version.get_version_tuple(), which stops at the
    first component that isn't a number, while a release number here is parsed
    whole, status included.
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
    """Return the five components of a version string, padding the numbers.

    Examples: (5, 2, 1, 'final', 0) for "5.2.1" and (2028, 0, 0, 'alpha', 1)
    for "2028a1".

    Calendar versions have no minor component, so this is not the shape
    django.VERSION uses for them, which get_django_version_tuple() returns.
    The zero kept here is what fills Release.micro.
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


def is_calendar_version(major):
    """Return True if this leading number is a calendar version year.

    A version string doesn't say which scheme it belongs to: "2028.1" is a
    well formed A.B version too. Only the year tells them apart, which is why
    this takes the number rather than reading a shape.
    """
    return major >= FIRST_CALENDAR_VERSION_YEAR


def get_main_version(version):
    """Return the main version (A.B[.C] or YYYY[.N]) from a version tuple.

    Django 6.2: replace with django.utils.version.get_main_version(), which
    then reads the numbers as version[:-2] and so needs no scheme of its own.
    Django 6.1's asserts a five component tuple and renders a zero patch
    number, giving "2028.0" for what we publish as "2028".
    """
    # The patch number is the last component of the main version and is
    # omitted when zero. It's the second component for calendar versions
    # (YYYY[.N]) and the third one for the earlier scheme (A.B[.C]).
    patch_index = 1 if is_calendar_version(version[0]) else 2
    parts = patch_index if version[patch_index] == 0 else patch_index + 1
    return ".".join(str(x) for x in version[:parts])


def get_feature_version(version):
    """Return the feature release version for a given version string."""
    components = get_loose_version_tuple(version)
    if is_calendar_version(components[0]):
        return str(components[0])
    return ".".join(str(component) for component in components[:2])


def get_next_feature_version(version):
    """Return the feature version following the given version string.

    Examples: "6.1" for "6.0.5", "2028" for "6.2.6" and "2029" for "2028.3".
    """
    version_tuple = get_version_tuple(version)
    major, minor, *_ = version_tuple
    if is_calendar_version(major):
        return str(major + 1)
    if (major, minor) == LAST_NON_CALENDAR_FEATURE_VERSION:
        return str(FIRST_CALENDAR_VERSION_YEAR)
    if minor < 2:
        return f"{major}.{minor + 1}"
    return f"{major + 1}.0"


def get_django_version_tuple(version):
    """Return the version tuple as django.VERSION spells it.

    Calendar versions have no minor component, so django.VERSION has four
    components for them, (year, patch, status, iteration), against five for
    the earlier scheme, (major, minor, micro, status, iteration). See DEP 20
    and django.utils.version.VersionTuple.

    Examples: (5, 2, 1, "final", 0) for "5.2.1" and (2028, 1, "final", 0) for
    "2028.1".

    Django 6.2: replace with django.utils.version.VersionTuple, which carries
    the shape itself and answers .feature and .patch under both schemes.
    """
    version_tuple = get_version_tuple(version)
    if not is_calendar_version(version_tuple[0]):
        return version_tuple
    # Drop the padding zero standing in for the missing minor component.
    year, patch, _, *rest = version_tuple
    return (year, patch, *rest)


def get_next_patch_version(version):
    """Return the django.VERSION tuple of the patch release following `version`.

    The status is "alpha" because Django's main branch carries the next,
    still unreleased, version.

    Examples: (5, 2, 4, "alpha", 0) for "5.2.3" and (2028, 1, "alpha", 0) for
    "2028".
    """
    version_tuple = get_version_tuple(version)
    major, minor, micro, *_ = version_tuple
    if is_calendar_version(major):
        return (major, minor + 1, "alpha", 0)
    return (major, minor, micro + 1, "alpha", 0)
