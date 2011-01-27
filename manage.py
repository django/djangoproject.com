#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if '--docs' in sys.argv:
    import django_website.settings.docs as settings
    sys.argv.remove('--docs')
else:
    import django_website.settings.www as settings
    
from django.core.management import execute_manager
execute_manager(settings)
