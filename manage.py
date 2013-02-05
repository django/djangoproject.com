#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if '--docs' in sys.argv:
        settings_module = 'django_docs.settings'
        sys.argv.remove('--docs')
    else:
        settings_module = 'django_www.settings'
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
