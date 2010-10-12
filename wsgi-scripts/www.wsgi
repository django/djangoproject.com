import os
import sys 
import site 

SITE_PACKAGES = '/home/www/djangoproject.com/lib/python2.6/site-packages'

# Remember original sys.path.
prev_sys_path = list(sys.path) 

# Add each new site-packages directory.
site.addsitedir(SITE_PACKAGES)

# Reorder sys.path so new directories at the front.
new_sys_path = [] 
for item in list(sys.path): 
    if item not in prev_sys_path: 
        new_sys_path.append(item) 
        sys.path.remove(item) 
sys.path[:0] = new_sys_path 

# Bootstrap Django
here = os.path.dirname(__file__)
parent = os.path.dirname(here)
sys.path.append(parent)
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_website.settings.www'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()