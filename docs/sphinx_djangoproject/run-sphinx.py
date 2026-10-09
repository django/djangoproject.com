#!/usr/bin/env python

# Run a single Sphinx build for a particular builder and language. This script
# is meant to be executed by build_doc_release. It is run in an isolated Python
# process to avoid import version conflicts between the docs being built and
# djangoproject.com's installed packages.
#
# The script:
# - Updates sys.path so the docs being built can import their own django.
# - Adds djangoproject.com's custom JSON builder extension to Sphinx config.
# - Runs the equivalent of sphinx-build for the given builder and language.

import argparse
import multiprocessing
import runpy
import sys
from pathlib import Path

from sphinx.application import Sphinx


def run_sphinx_build(
    *,
    checkout_dir,
    source_dir,
    build_dir,
    doctree_dir,
    builder,
    language,
):
    # Do not try to import django directly in this script. That would cause
    # inconsistent builds when docs/conf.py tries to import its own django.
    assert "django" not in sys.modules

    # Make sure docs/conf.py can import django from its own source.
    sys.path.insert(0, str(checkout_dir))

    # Add djangoproject.com's JSON builder extension to existing extensions in
    # the conf.py of the docs version being built.
    conf_globals = runpy.run_path(str(source_dir / "conf.py"))
    extensions = [
        *conf_globals.get("extensions", []),
        "sphinx_djangoproject.builder",
    ]

    # Make sure Sphinx can import sphinx_djangoproject.builder from here. Avoid
    # polluting the import space by using a unique module name and placing
    # djangoproject/docs at the lowest priority in sys.path.
    djangoproject_docs_dir = Path(__file__).resolve().parent.parent
    sys.path.append(str(djangoproject_docs_dir))

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
    parser.add_argument("--checkout-dir", required=True, type=Path)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--doctree-dir", required=True, type=Path)
    parser.add_argument("--builder", required=True)
    parser.add_argument("--language", required=True)
    args = parser.parse_args()

    run_sphinx_build(
        checkout_dir=args.checkout_dir.resolve(),
        source_dir=args.source_dir.resolve(),
        build_dir=args.build_dir.resolve(),
        doctree_dir=args.doctree_dir.resolve(),
        builder=args.builder,
        language=args.language,
    )


if __name__ == "__main__":
    main()
