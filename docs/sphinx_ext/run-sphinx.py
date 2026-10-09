#!/usr/bin/env python

# Run a single Sphinx build for a particular builder and language. This script
# is meant to be executed by build_doc_release. It is run in an isolated Python
# process to avoid import version conflicts between the docs being built and
# djangoproject.com's installed packages.
#
# The script runs the equivalent of sphinx-build for the given builder and
# language, injecting djangoproject.com's custom JSON builder extension into
# the Sphinx config.

import argparse
import multiprocessing
import runpy
import sys
from pathlib import Path

from sphinx.application import Sphinx


def run_sphinx_build(
    *,
    source_dir,
    build_dir,
    doctree_dir,
    builder,
    language,
):
    # Do not try to import django directly in this script. That would cause
    # inconsistent builds when docs/conf.py tries to import its own django.
    if "django" in sys.modules:
        raise RuntimeError(
            "django was imported before run_sphinx_build(); docs/conf.py "
            "would pick up the wrong version."
        )

    # Add djangoproject.com's JSON builder extension to existing extensions in
    # the conf.py of the docs version being built. (This causes conf.py to be
    # executed twice: once here and again when Sphinx loads it below. Note that
    # Django's conf.py updates sys.path so it can import its own django and
    # local Sphinx extensions. These duplicate sys.path entries bracket the
    # extension_dir addition below, and do not cause problems.)
    conf_globals = runpy.run_path(str(source_dir / "conf.py"))
    extensions = [
        *conf_globals.get("extensions", []),
        "python_objects_json_html_builder",
    ]

    # Make sure Sphinx can import python_objects_json_html_builder from here.
    extension_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(extension_dir))

    app = Sphinx(
        srcdir=source_dir,
        confdir=source_dir,
        outdir=build_dir,
        doctreedir=doctree_dir,
        buildername=builder,
        # Translated docs builds generate a lot of warnings, so send stderr
        # to stdout to be logged rather than generating an email.
        warning=sys.stdout,
        parallel=multiprocessing.cpu_count(),
        verbosity=0,
        confoverrides={
            "language": language,
            "extensions": extensions,
        },
    )
    app.build()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--doctree-dir", required=True, type=Path)
    parser.add_argument("--builder", required=True)
    parser.add_argument("--language", required=True)
    args = parser.parse_args()

    run_sphinx_build(
        source_dir=args.source_dir.resolve(),
        build_dir=args.build_dir.resolve(),
        doctree_dir=args.doctree_dir.resolve(),
        builder=args.builder,
        language=args.language,
    )


if __name__ == "__main__":
    main()
