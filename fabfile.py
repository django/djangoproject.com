import unipath
from fabric.api import *
from fabric.contrib import files

# Fab settings
env.hosts = ['ve.djangoproject.com']

# Deployment environment paths and settings and such.
env.deploy_base = unipath.Path('/home/www/djangoproject.com')
env.virtualenv = env.deploy_base
env.code_dir = env.deploy_base.child('src')
env.git_url = 'git://github.com/jacobian/djangoproject.com.git'

# FIXME: make a deploy branch in this repo to deploy against.
env.default_deploy_ref = 'origin/community_redux'

def deploy():
    """
    Full deploy: new code, update dependencies, migrate, and restart services.
    """
    deploy_code()
    update_dependencies()
    # migrate()
    # apache("restart")
    # memcached("restart")

def quick_deploy():
    """
    Quick deploy: new code and an in-place reload.
    """
    deploy_code()
    # apache("reload")

def deploy_code(ref=None):
    """
    Update code on the servers from Git.    
    """
    ref = ref or env.default_deploy_ref
    puts("Deploying %s" % ref)
    if not files.exists(env.code_dir):
        sudo('git clone %s %s' % (env.git_url, env.code_dir))
    with cd(env.code_dir):
        sudo('git fetch && git reset --hard %s' % ref)

def update_dependencies():
    """
    Update dependencies in the virtualenv.
    """
    pip = env.virtualenv.child('bin', 'pip')
    reqs = env.code_dir.child('deploy-requirements.txt')
    sudo('%s -q install -r %s' % (pip, reqs))

def _managepy(cmd, site='www'):
    """
    Helper: run a management command remotely.
    """
    django_admin = env.virtualenv.child('bin', 'django-admin.py')
    

def copy_db():
    """
    Copy the production DB locally for testing.
    """
    local('ssh %s pg_dump -U djangoproject -c djangoproject | psql djangoproject' % env.hosts[0])